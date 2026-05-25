"""Import tools — VSDX upload and image-to-diagram conversion."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from visio_mcp._state import mcp, _diagram, _layout, _waf, _caf
from visio_mcp.azure_catalog import (
    AZURE_SHAPE_CATALOG,
    resolve_alias,
    search_shapes,
)
from visio_mcp.caf_validator import CafValidator, CAF_NAMING_PREFIXES
from visio_mcp.layout_engine import LayoutEngine
from visio_mcp.models import WafPillar
from visio_mcp.waf_validator import WafValidator

logger = logging.getLogger(__name__)

# IMPORT TOOLS — VSDX upload + Image-to-Diagram
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def import_vsdx(
    file_path: str,
    page: int | str = "all",
    assess_waf: bool = True,
    assess_caf: bool = True,
) -> dict[str, Any]:
    """Import an existing Visio .vsdx file, parse its shapes into the current diagram,
    and optionally run WAF/CAF assessment.

    This reads the .vsdx via Visio COM, extracts all shapes (matching them to known
    Azure resource types), connections, and boundary rectangles, then populates
    the diagram state so you can build on top of it.

    Supports multi-page/tab Visio files. By default imports all pages.

    Args:
        file_path: Absolute or relative path to the .vsdx file to import.
        page: Which page(s) to import. Options:
              - "all" (default): Import all pages/tabs.
              - "list": Return page names and counts without importing.
              - An integer (1-based): Import only that page number.
        assess_waf: Run WAF validation after import (default True).
        assess_caf: Run CAF validation after import (default True).

    Returns:
        Summary of imported resources, connections, boundaries, and validation results.
    """
    import re

    file_path = os.path.abspath(file_path)
    if not os.path.isfile(file_path):
        return {"status": "error", "message": f"File not found: {file_path}"}
    if not file_path.lower().endswith((".vsdx", ".vsd")):
        return {"status": "error", "message": "File must be a .vsdx or .vsd file."}

    # Build a lookup from display name fragments → resource_type
    _name_to_type: dict[str, str] = {}
    for key, info in AZURE_SHAPE_CATALOG.items():
        _name_to_type[info.display_name.lower()] = key
        # Also map the key itself (underscores → spaces)
        _name_to_type[key.replace("_", " ")] = key

    def _guess_resource_type(shape_text: str, master_name: str = "") -> str | None:
        """Try to match a shape's text/master to a known Azure resource type."""
        candidates = [shape_text.lower().strip(), master_name.lower().strip()]
        for candidate in candidates:
            if not candidate:
                continue
            # Exact match
            if candidate in _name_to_type:
                return _name_to_type[candidate]
            # Key match (e.g. "app_service")
            key_form = candidate.replace(" ", "_").replace("-", "_")
            if key_form in AZURE_SHAPE_CATALOG:
                return key_form
            # Substring match — check if any catalog name is IN the shape text
            for name, rtype in _name_to_type.items():
                if len(name) > 3 and (name in candidate or candidate in name):
                    return rtype
        # Common patterns in diagram text
        t = shape_text.lower()
        if "pe:" in t or "private endpoint" in t:
            return "private_endpoint"
        if "openai" in t or "gpt" in t:
            return "openai_service"
        if "foundry" in t or "agent service" in t:
            return "cognitive_services"
        if "storage" in t and "data lake" not in t:
            return "storage_account"
        if "cosmos" in t:
            return "cosmos_db"
        if "sql" in t and "managed" in t:
            return "sql_managed_instance"
        if "sql" in t:
            return "sql_database"
        if "redis" in t or "cache" in t:
            return "redis_cache"
        if "key vault" in t or "keyvault" in t:
            return "key_vault"
        if "firewall" in t:
            return "firewall"
        if "gateway" in t and "vpn" in t:
            return "vpn_gateway"
        if "gateway" in t and "app" in t:
            return "application_gateway"
        if "bastion" in t:
            return "bastion"
        if "container" in t and "registry" in t:
            return "container_registry"
        if "container" in t and "app" in t:
            return "container_apps"
        if "function" in t:
            return "function_app"
        if "app service" in t or "web app" in t:
            return "app_service"
        if "vm" in t or "virtual machine" in t:
            return "virtual_machine"
        if "load balancer" in t:
            return "load_balancer"
        if "monitor" in t:
            return "monitor"
        if "log analytics" in t:
            return "log_analytics"
        if "insight" in t:
            return "application_insights"
        if "search" in t and "ai" in t:
            return "ai_search"
        if "entra" in t or "active directory" in t or "aad" in t:
            return "entra_id"
        if "managed identity" in t:
            return "managed_identity"
        if "policy" in t:
            return "policy"
        if "sentinel" in t:
            return "sentinel"
        if "defender" in t:
            return "defender_for_cloud"
        return None

    def _guess_boundary_type(text: str) -> str:
        """Guess boundary type from shape text."""
        t = text.lower()
        if "subnet" in t or "snet" in t:
            return "subnet"
        if "vnet" in t or "virtual network" in t:
            return "vnet"
        if "resource group" in t or "rg-" in t:
            return "resource_group"
        if "subscription" in t:
            return "subscription"
        if "management group" in t:
            return "management_group"
        if "nsg" in t or "network security" in t:
            return "nsg"
        if "region" in t or "availability zone" in t:
            return "availability_zone"
        return "resource_group"

    try:
        import pythoncom
        pythoncom.CoInitialize()
    except Exception:
        pass

    try:
        import win32com.client
    except ImportError:
        return {"status": "error", "message": "win32com not available — Visio COM required for .vsdx import."}

    # Kill orphaned Visio
    import subprocess
    try:
        subprocess.run(["taskkill", "/F", "/IM", "VISIO.EXE"], capture_output=True, timeout=10)
    except Exception:
        pass

    app = None
    try:
        app = win32com.client.Dispatch("Visio.Application")
        app.Visible = False
        app.AlertResponse = 6
        doc = app.Documents.Open(file_path)

        total_pages = doc.Pages.Count

        # "list" mode — return page info without importing
        if isinstance(page, str) and page.lower() == "list":
            page_info = []
            for pi in range(1, total_pages + 1):
                pg = doc.Pages(pi)
                page_info.append({
                    "page_number": pi,
                    "name": pg.Name,
                    "shape_count": pg.Shapes.Count,
                })
            doc.Close()
            return {
                "status": "page_list",
                "file_path": file_path,
                "total_pages": total_pages,
                "pages": page_info,
            }

        # Determine which pages to import
        if isinstance(page, str) and page.lower() == "all":
            page_numbers = list(range(1, total_pages + 1))
        else:
            page_num = int(page)
            if page_num < 1 or page_num > total_pages:
                doc.Close()
                return {
                    "status": "error",
                    "message": f"Page {page_num} out of range. File has {total_pages} page(s).",
                }
            page_numbers = [page_num]

        # Parse shapes from selected pages
        resources_found = []
        boundaries_found = []
        connectors_found = []
        page_names = []

        for page_idx in page_numbers:
            pg = doc.Pages(page_idx)
            page_names.append(pg.Name)
            # Prefix for IDs to avoid collisions across pages
            prefix = f"p{page_idx}-" if len(page_numbers) > 1 else ""

            for i in range(1, pg.Shapes.Count + 1):
                shape = pg.Shapes(i)
                text = (shape.Text or "").strip()
            if not text:
                continue

            # Check if it's a connector (1-D shape)
            try:
                is_1d = shape.OneD != 0
            except Exception:
                is_1d = False

            if is_1d:
                # It's a connector
                try:
                    begin_connects = shape.Connects
                    src_id = None
                    tgt_id = None
                    for j in range(1, begin_connects.Count + 1):
                        conn = begin_connects(j)
                        connected_shape = conn.ToSheet
                        c_text = (connected_shape.Text or "").strip()
                        if j == 1:
                            src_id = c_text
                        else:
                            tgt_id = c_text
                    if src_id and tgt_id:
                        connectors_found.append({
                            "source_text": src_id,
                            "target_text": tgt_id,
                            "label": text if text != src_id and text != tgt_id else "",
                            "page": page_idx,
                            "prefix": prefix,
                        })
                except Exception:
                    pass
                continue

            # Get position and size
            try:
                px = shape.Cells("PinX").ResultIU
                py = shape.Cells("PinY").ResultIU
                w = shape.Cells("Width").ResultIU
                h = shape.Cells("Height").ResultIU
            except Exception:
                px, py, w, h = 5.0, 5.0, 1.0, 1.0

            # Skip tiny shapes (step number circles, decorative elements)
            if w < 0.5 and h < 0.5:
                continue
            # Skip shapes that are just a number (step circles)
            if text.isdigit():
                continue
            # Skip title-like shapes at the very top (full-width, thin)
            if w > 8.0 and h < 0.8:
                continue

            # Get master name for type matching
            master_name = ""
            try:
                if shape.Master:
                    master_name = shape.Master.Name or ""
            except Exception:
                pass

            # Determine if this is a boundary (large rectangle) or resource
            is_boundary = w > 3.0 and h > 2.0 and not master_name

            if is_boundary:
                btype = _guess_boundary_type(text)
                boundaries_found.append({
                    "text": text,
                    "boundary_type": btype,
                    "x": px - w / 2,
                    "y": py - h / 2,
                    "width": w,
                    "height": h,
                    "page": page_idx,
                    "prefix": prefix,
                })
            else:
                rtype = _guess_resource_type(text, master_name)
                resources_found.append({
                    "text": text,
                    "resource_type": rtype or "generic",
                    "master_name": master_name,
                    "x": px,
                    "y": py,
                    "width": w,
                    "height": h,
                    "page": page_idx,
                    "prefix": prefix,
                })

        doc.Close()
    except Exception as e:
        return {"status": "error", "message": f"Failed to read .vsdx: {e}"}
    finally:
        if app:
            try:
                app.Quit()
            except Exception:
                pass

    # Populate diagram state
    diagram_name = Path(file_path).stem.replace("_", " ").replace("-", " ").title()
    if len(page_names) == 1:
        diagram_name = f"{diagram_name} — {page_names[0]}"
    _diagram.new_diagram(diagram_name)
    # Store page metadata on the state for preview/validators
    _diagram.state.properties["pages"] = [
        {"number": pn, "name": page_names[idx]}
        for idx, pn in enumerate(page_numbers)
    ]

    # For multi-page imports, offset each page's Y position so they don't overlap
    page_y_offsets: dict[int, float] = {}
    if len(page_numbers) > 1:
        y_offset = 0.0
        for pidx in page_numbers:
            page_y_offsets[pidx] = y_offset
            # Find max Y extent on this page
            max_y = 0.0
            for b in boundaries_found:
                if b["page"] == pidx:
                    max_y = max(max_y, b["y"] + b["height"])
            for r in resources_found:
                if r["page"] == pidx:
                    max_y = max(max_y, r["y"] + r.get("height", 1.0))
            y_offset += max_y + 2.0  # 2-inch gap between pages
    else:
        for pidx in page_numbers:
            page_y_offsets[pidx] = 0.0

    # Add boundaries
    text_to_bid: dict[str, str] = {}
    for i, b in enumerate(boundaries_found):
        bid = f"{b['prefix']}imported-boundary-{i}"
        y_off = page_y_offsets.get(b["page"], 0.0)
        _page_name = page_names[page_numbers.index(b["page"])] if b["page"] in page_numbers else ""
        _diagram.add_boundary(
            boundary_type=b["boundary_type"],
            display_name=b["text"],
            boundary_id=bid,
            x=b["x"], y=b["y"] + y_off,
            width=b["width"], height=b["height"],
            properties={"page": b["page"], "page_name": _page_name},
        )
        # Key by prefix+text to handle same name on different pages
        text_to_bid[b["prefix"] + b["text"]] = bid

    # Add resources
    text_to_rid: dict[str, str] = {}
    for i, r in enumerate(resources_found):
        rid = f"{r['prefix']}imported-resource-{i}"
        rtype = r["resource_type"]
        if rtype == "generic":
            rtype = "app_service"  # safe fallback

        y_off = page_y_offsets.get(r["page"], 0.0)
        _page_name = page_names[page_numbers.index(r["page"])] if r["page"] in page_numbers else ""
        _diagram.add_resource(
            resource_type=rtype,
            display_name=r["text"],
            resource_id=rid,
            x=r["x"], y=r["y"] + y_off,
            properties={"page": r["page"], "page_name": _page_name},
        )
        text_to_rid[r["prefix"] + r["text"]] = rid

        # Auto-assign to containing boundary (same page only)
        for b in boundaries_found:
            if b["page"] != r["page"]:
                continue
            bx1, by1 = b["x"], b["y"]
            bx2, by2 = bx1 + b["width"], by1 + b["height"]
            if bx1 <= r["x"] <= bx2 and by1 <= r["y"] <= by2:
                bid = text_to_bid[b["prefix"] + b["text"]]
                _diagram.assign_to_boundary(rid, bid)
                break

    # Add connections (match within same page)
    connection_count = 0
    for c in connectors_found:
        src_rid = text_to_rid.get(c["prefix"] + c["source_text"])
        tgt_rid = text_to_rid.get(c["prefix"] + c["target_text"])
        if src_rid and tgt_rid:
            try:
                _diagram.add_connection(
                    source_id=src_rid,
                    target_id=tgt_rid,
                    label=c["label"],
                    connection_type="data_flow",
                )
                connection_count += 1
            except ValueError:
                pass

    # Run assessments
    waf_result = None
    caf_result = None
    if assess_waf:
        waf_report = _waf.validate(_diagram.state)
        waf_result = {
            "score": waf_report.score,
            "summary": waf_report.summary,
            "findings_count": len(waf_report.findings),
            "top_findings": [
                {"severity": f.severity, "pillar": f.pillar, "message": f.message, "recommendation": f.recommendation, "page": f.page, "page_name": f.page_name or ""}
                for f in waf_report.findings[:10]
            ],
        }
    if assess_caf:
        caf_report = _caf.validate(_diagram.state)
        caf_result = {
            "score": caf_report.score,
            "summary": caf_report.summary,
            "findings_count": len(caf_report.findings),
            "top_findings": [
                {"severity": f.severity, "pillar": f.pillar, "message": f.message, "recommendation": f.recommendation, "page": f.page, "page_name": f.page_name or ""}
                for f in caf_report.findings[:10]
            ],
        }

    return {
        "status": "imported",
        "name": diagram_name,
        "file_path": file_path,
        "pages_imported": len(page_numbers),
        "page_names": page_names,
        "resources_imported": len(resources_found),
        "boundaries_imported": len(boundaries_found),
        "connections_imported": connection_count,
        "unmatched_resources": [
            r["text"] for r in resources_found if r["resource_type"] == "generic"
        ],
        "waf_assessment": waf_result,
        "caf_assessment": caf_result,
    }


def _import_svg_as_text(file_path: str, preserve_original_style: bool = False) -> dict[str, Any]:
    """Analyze an SVG file as structured XML text and convert to an Azure diagram.

    SVGs contain readable text labels and structure that an LLM can parse
    directly without needing a vision model.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            svg_text = f.read()
    except Exception as e:
        return {"status": "error", "message": f"Failed to read SVG file: {e}"}

    # Truncate very large SVGs to stay within token limits
    max_chars = 60_000
    truncated = len(svg_text) > max_chars
    if truncated:
        svg_text = svg_text[:max_chars]

    catalog_keys = sorted(AZURE_SHAPE_CATALOG.keys())

    if preserve_original_style:
        text_prompt = f"""Analyze this SVG diagram. The SVG source contains text labels, \
group structures, and shapes. Identify all components and connections.

Preserve the EXACT labels, colors, and visual style from the SVG. Do NOT map to Azure services.

For each component, extract its visual appearance from the SVG:
- shape: rectangle, rounded_rectangle, diamond, circle, hexagon, parallelogram, cylinder, cloud, person, gear, document, arrow_box
- fill_color: hex color from the SVG fill attribute
- border_color: hex color from the SVG stroke attribute
- text_color: hex color of the text element

Return a JSON object with this exact structure (no markdown fencing):
{{
  "diagram_name": "descriptive name for this diagram",
  "resources": [
    {{"id": "unique-id", "display_name": "Exact Label from SVG", "shape": "rectangle", "fill_color": "#FFFFFF", "border_color": "#000000", "text_color": "#000000", "x": 5.0, "y": 3.0}}
  ],
  "boundaries": [
    {{"id": "unique-id", "boundary_type": "resource_group", "display_name": "Group Label", "fill_color": "#F5F5F5", "border_color": "#9E9E9E", "x": 1.0, "y": 1.0, "width": 8.0, "height": 6.0}}
  ],
  "connections": [
    {{"source_id": "resource-id-1", "target_id": "resource-id-2", "label": "connection label", "line_style": "solid|dashed|dotted", "connection_type": "data_flow|dependency|network"}}
  ]
}}

Rules:
- x/y coordinates should approximate the spatial layout (in inches, 0-20 range)
- Preserve ALL text labels EXACTLY as they appear in the SVG
- Extract colors directly from SVG fill/stroke attributes
- Identify grouping rectangles as boundaries
- Identify lines/paths between components as connections
{"- NOTE: SVG was truncated due to size; analyze what is available." if truncated else ""}

SVG source:
{svg_text}"""
    else:
        text_prompt = f"""Analyze this SVG architecture diagram. The SVG source contains text labels, \
group structures, and shapes that represent an architecture. Identify all components and connections.

For each component, determine the closest Azure resource type from this catalog:
{', '.join(catalog_keys)}

Return a JSON object with this exact structure (no markdown fencing):
{{
  "diagram_name": "descriptive name for this architecture",
  "resources": [
    {{"id": "unique-id", "resource_type": "catalog_key", "display_name": "Label from SVG", "x": 5.0, "y": 3.0}}
  ],
  "boundaries": [
    {{"id": "unique-id", "boundary_type": "vnet|subnet|resource_group|subscription|region", "display_name": "Label", "x": 1.0, "y": 1.0, "width": 8.0, "height": 6.0}}
  ],
  "connections": [
    {{"source_id": "resource-id-1", "target_id": "resource-id-2", "label": "connection label", "connection_type": "data_flow|dependency|network"}}
  ]
}}

Rules:
- x/y coordinates should approximate the spatial layout (in inches, 0-20 range)
- Use the EXACT resource_type keys from the catalog list above
- If a component doesn't match any Azure service, use the closest match
- Identify grouping rectangles as boundaries (VNets, subnets, resource groups)
- Identify lines/paths between components as connections
- Preserve all text labels from the SVG
{"- NOTE: SVG was truncated due to size; analyze what is available." if truncated else ""}

SVG source:
{svg_text}"""

    from openai import OpenAI

    github_token = os.environ.get("GITHUB_TOKEN")
    openai_key = os.environ.get("OPENAI_API_KEY")
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

    if github_token:
        client = OpenAI(base_url="https://models.inference.ai.azure.com", api_key=github_token)
        model = os.environ.get("GITHUB_MODELS_MODEL", "gpt-4o")
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    elif azure_endpoint:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
            api_version="2024-12-01-preview",
        )
        model = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    else:
        return {"status": "error", "message": "No AI provider configured. Set GITHUB_TOKEN, OPENAI_API_KEY, or AZURE_OPENAI_ENDPOINT."}

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": text_prompt}],
            max_tokens=4000,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        return {"status": "error", "message": f"AI analysis failed: {e}"}

    import re as _re
    raw = _re.sub(r"^```(?:json)?\s*", "", raw)
    raw = _re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Failed to parse AI response: {e}", "raw_response": raw[:2000]}

    # Populate diagram state (same logic as raster import)
    diagram_name = parsed.get("diagram_name", "Imported SVG Diagram")
    _diagram.new_diagram(diagram_name)

    boundary_count = 0
    for b in parsed.get("boundaries", []):
        btype = b.get("boundary_type", "resource_group")
        if btype not in BOUNDARY_STYLES:
            btype = "resource_group"
        _diagram.add_boundary(
            boundary_type=btype,
            display_name=b.get("display_name", f"Boundary {boundary_count}"),
            boundary_id=b.get("id", f"svg-boundary-{boundary_count}"),
            x=b.get("x", 1.0), y=b.get("y", 1.0),
            width=b.get("width", 5.0), height=b.get("height", 4.0),
        )
        boundary_count += 1

    resource_count = 0
    for r in parsed.get("resources", []):
        if preserve_original_style:
            rtype = "general"
            if rtype not in AZURE_SHAPE_CATALOG:
                rtype = "app_service"
            metadata = {
                "original_shape": r.get("shape", "rectangle"),
                "fill_color": r.get("fill_color", "#FFFFFF"),
                "border_color": r.get("border_color", "#000000"),
                "text_color": r.get("text_color", "#000000"),
                "preserve_style": True,
            }
            _diagram.add_resource(
                resource_type=rtype,
                display_name=r.get("display_name", f"Resource {resource_count}"),
                resource_id=r.get("id", f"svg-resource-{resource_count}"),
                x=r.get("x", 5.0), y=r.get("y", 5.0),
                properties=metadata,
            )
        else:
            rtype = r.get("resource_type", "app_service")
            if rtype not in AZURE_SHAPE_CATALOG:
                rtype = "app_service"
            _diagram.add_resource(
                resource_type=rtype,
                display_name=r.get("display_name", f"Resource {resource_count}"),
                resource_id=r.get("id", f"svg-resource-{resource_count}"),
                x=r.get("x", 5.0), y=r.get("y", 5.0),
            )
        resource_count += 1

    connection_count = 0
    for c in parsed.get("connections", []):
        ctype = c.get("connection_type", "data_flow")
        if ctype not in CONNECTOR_STYLES:
            ctype = "data_flow"
        try:
            _diagram.add_connection(
                source_id=c["source_id"],
                target_id=c["target_id"],
                label=c.get("label", ""),
                connection_type=ctype,
            )
            connection_count += 1
        except (ValueError, KeyError):
            pass

    if not preserve_original_style:
        try:
            _layout.auto_layout(_diagram.state, strategy="tiered")
        except Exception:
            pass

    return {
        "status": "imported",
        "name": diagram_name,
        "file_path": file_path,
        "resources_created": resource_count,
        "boundaries_created": boundary_count,
        "connections_created": connection_count,
        "analysis_method": "text",
        "vision_model": model,
        "components_identified": parsed,
    }


@mcp.tool()
def import_image(
    file_path: str,
    preserve_original_style: bool = False,
) -> dict[str, Any]:
    """Import an image (screenshot, whiteboard photo, block diagram) and convert it
    to an Azure architecture diagram by identifying blocks/labels in the image.

    Uses GPT-4o vision to analyze the image, identify named components, and map them
    to Azure resource types. Creates a new diagram with the identified resources,
    boundaries, and connections.

    Supported formats: PNG, JPG, JPEG, BMP, GIF, WEBP, TIFF, SVG.

    SVG files are analyzed as structured XML text (no vision model needed).
    All raster formats are analyzed using GPT-4o vision.

    Args:
        file_path: Absolute or relative path to the image file.
        preserve_original_style: When True, keeps the original formatting, shapes,
            colors, and labels from the image instead of converting to Azure stencil
            icons. Useful for flowcharts, process diagrams, and custom visuals.

    Returns:
        Summary of identified components and the created diagram.
    """
    import base64

    file_path = os.path.abspath(file_path)
    if not os.path.isfile(file_path):
        return {"status": "error", "message": f"File not found: {file_path}"}

    ext = Path(file_path).suffix.lower()
    supported = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff", ".svg")
    if ext not in supported:
        return {"status": "error", "message": f"Unsupported image format: {ext}. Use PNG, JPG, BMP, GIF, WEBP, TIFF, or SVG."}

    # SVG files are XML text — analyze as text instead of vision
    if ext == ".svg":
        return _import_svg_as_text(file_path, preserve_original_style=preserve_original_style)

    # Read and encode raster image
    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    mime_map = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".bmp": "image/bmp", ".gif": "image/gif", ".webp": "image/webp",
        ".tif": "image/tiff", ".tiff": "image/tiff",
    }
    mime_type = mime_map.get(ext, "image/png")

    # Build the catalog reference for the prompt
    catalog_keys = sorted(AZURE_SHAPE_CATALOG.keys())

    if preserve_original_style:
        vision_prompt = """Analyze this architecture/flow diagram image. Identify all components (boxes, shapes, icons, labels) and their connections.

Preserve the EXACT labels, colors, and visual style from the image. Do NOT map to Azure services.

For each component, describe its visual appearance:
- shape: rectangle, rounded_rectangle, diamond, circle, hexagon, parallelogram, cylinder, cloud, person, gear, document, arrow_box
- fill_color: hex color of the shape fill (e.g., "#4CAF50", "#2196F3")
- border_color: hex color of the shape border
- text_color: hex color of the text label

Return a JSON object with this exact structure (no markdown fencing):
{{
  "diagram_name": "descriptive name for this diagram",
  "resources": [
    {{"id": "unique-id", "display_name": "Exact Label from image", "shape": "rectangle", "fill_color": "#FFFFFF", "border_color": "#000000", "text_color": "#000000", "x": 5.0, "y": 3.0}}
  ],
  "boundaries": [
    {{"id": "unique-id", "boundary_type": "resource_group", "display_name": "Group Label", "fill_color": "#F5F5F5", "border_color": "#9E9E9E", "x": 1.0, "y": 1.0, "width": 8.0, "height": 6.0}}
  ],
  "connections": [
    {{"source_id": "resource-id-1", "target_id": "resource-id-2", "label": "connection label", "line_style": "solid|dashed|dotted", "connection_type": "data_flow|dependency|network"}}
  ]
}}

Rules:
- x/y coordinates should approximate the spatial layout in the image (in inches, 0-20 range)
- Preserve ALL text labels EXACTLY as they appear in the image
- Identify grouping/container boxes as boundaries
- Identify arrows/lines as connections (note if dashed, dotted, or solid)
- Capture the fill color of each shape as accurately as possible
- For decision diamonds, use shape "diamond"
- For people/user icons, use shape "person"
- For process/gear icons, use shape "gear" """
    else:
        vision_prompt = f"""Analyze this architecture diagram image. Identify all components (boxes, icons, labels) and their connections.

For each component, determine the closest Azure resource type from this catalog:
{', '.join(catalog_keys)}

Return a JSON object with this exact structure (no markdown fencing):
{{
  "diagram_name": "descriptive name for this architecture",
  "resources": [
    {{"id": "unique-id", "resource_type": "catalog_key", "display_name": "Label from image", "x": 5.0, "y": 3.0}}
  ],
  "boundaries": [
    {{"id": "unique-id", "boundary_type": "vnet|subnet|resource_group|subscription|region", "display_name": "Label", "x": 1.0, "y": 1.0, "width": 8.0, "height": 6.0}}
  ],
  "connections": [
    {{"source_id": "resource-id-1", "target_id": "resource-id-2", "label": "connection label", "connection_type": "data_flow|dependency|network"}}
  ]
}}

Rules:
- x/y coordinates should approximate the spatial layout in the image (in inches, 0-20 range)
- Use the EXACT resource_type keys from the catalog list above
- If a component doesn't match any Azure service, use the closest match
- Identify grouping boxes as boundaries (VNets, subnets, resource groups)
- Identify arrows/lines as connections
- Preserve all text labels from the image"""

    # Call the vision model
    from openai import OpenAI

    github_token = os.environ.get("GITHUB_TOKEN")
    openai_key = os.environ.get("OPENAI_API_KEY")
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

    if github_token:
        client = OpenAI(base_url="https://models.inference.ai.azure.com", api_key=github_token)
        model = os.environ.get("GITHUB_MODELS_MODEL", "gpt-4o")
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    elif azure_endpoint:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
            api_version="2024-12-01-preview",
        )
        model = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    else:
        return {"status": "error", "message": "No AI provider configured. Set GITHUB_TOKEN, OPENAI_API_KEY, or AZURE_OPENAI_ENDPOINT."}

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}},
                    ],
                }
            ],
            max_tokens=4000,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        return {"status": "error", "message": f"Vision API call failed: {e}"}

    # Parse the JSON response (strip markdown fencing if present)
    import re
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "message": f"Failed to parse vision model response: {e}",
            "raw_response": raw[:2000],
        }

    # Populate diagram state
    diagram_name = parsed.get("diagram_name", "Imported Diagram")
    _diagram.new_diagram(diagram_name)

    boundary_count = 0
    for b in parsed.get("boundaries", []):
        btype = b.get("boundary_type", "resource_group")
        if btype not in BOUNDARY_STYLES:
            btype = "resource_group"
        _diagram.add_boundary(
            boundary_type=btype,
            display_name=b.get("display_name", f"Boundary {boundary_count}"),
            boundary_id=b.get("id", f"img-boundary-{boundary_count}"),
            x=b.get("x", 1.0), y=b.get("y", 1.0),
            width=b.get("width", 5.0), height=b.get("height", 4.0),
        )
        boundary_count += 1

    resource_count = 0
    for r in parsed.get("resources", []):
        if preserve_original_style:
            # Use a generic resource type but store original style in metadata
            rtype = "general"
            if rtype not in AZURE_SHAPE_CATALOG:
                rtype = "app_service"
            metadata = {
                "original_shape": r.get("shape", "rectangle"),
                "fill_color": r.get("fill_color", "#FFFFFF"),
                "border_color": r.get("border_color", "#000000"),
                "text_color": r.get("text_color", "#000000"),
                "preserve_style": True,
            }
            _diagram.add_resource(
                resource_type=rtype,
                display_name=r.get("display_name", f"Resource {resource_count}"),
                resource_id=r.get("id", f"img-resource-{resource_count}"),
                x=r.get("x", 5.0), y=r.get("y", 5.0),
                properties=metadata,
            )
        else:
            rtype = r.get("resource_type", "app_service")
            if rtype not in AZURE_SHAPE_CATALOG:
                rtype = "app_service"
            _diagram.add_resource(
                resource_type=rtype,
                display_name=r.get("display_name", f"Resource {resource_count}"),
                resource_id=r.get("id", f"img-resource-{resource_count}"),
                x=r.get("x", 5.0), y=r.get("y", 5.0),
            )
        resource_count += 1

    connection_count = 0
    for c in parsed.get("connections", []):
        ctype = c.get("connection_type", "data_flow")
        if ctype not in CONNECTOR_STYLES:
            ctype = "data_flow"
        try:
            line_style = "solid"
            if preserve_original_style:
                line_style = c.get("line_style", "solid")
            _diagram.add_connection(
                source_id=c["source_id"],
                target_id=c["target_id"],
                label=c.get("label", ""),
                connection_type=ctype,
                style=line_style,
            )
            connection_count += 1
        except (ValueError, KeyError):
            pass

    # Auto-layout only when converting to Azure stencils (preserve positions otherwise)
    if not preserve_original_style:
        try:
            _layout.auto_layout(_diagram.state, strategy="tiered")
        except Exception:
            pass
    else:
        # Store source image path for background trace embedding during export
        _diagram.state.properties["source_image_path"] = str(Path(file_path).resolve())
        _diagram.state.properties["preserve_original_style"] = True

    return {
        "status": "imported",
        "name": diagram_name,
        "file_path": file_path,
        "resources_created": resource_count,
        "boundaries_created": boundary_count,
        "connections_created": connection_count,
        "analysis_method": "vision",
        "vision_model": model,
        "preserve_original_style": preserve_original_style,
        "components_identified": parsed,
    }


# ═══════════════════════════════════════════════════════════════════
