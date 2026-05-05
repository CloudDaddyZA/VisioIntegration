"""MCP server exposing tools for Azure architecture diagram creation in Visio.

Diagrams align with Microsoft Azure Architecture Center standards:
  - Official Azure SVG icons (no crop/flip/rotate)
  - Reference architecture patterns from Architecture Center
  - WAF and CAF framework validation
  - Microsoft diagram conventions (numbered workflow steps, boundary grouping)

Run with:  python -m visio_mcp.server
Or:        visio-mcp  (if installed via pip)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .azure_catalog import (
    AZURE_SHAPE_CATALOG,
    BOUNDARY_STYLES,
    CONNECTOR_STYLES,
    list_categories,
    resolve_alias,
    search_shapes,
)
from .caf_validator import CafValidator, CAF_NAMING_PREFIXES
from .diagram_state import DiagramManager
from .layout_engine import LayoutEngine
from .models import WafPillar
from .reference_architectures import (
    AZURE_DIAGRAM_COLORS,
    REFERENCE_ARCHITECTURES,
    get_reference_architecture,
    list_reference_architectures,
    search_reference_architectures,
    list_architecture_styles,
    get_architecture_style,
    suggest_style_for_description,
    list_design_patterns,
    get_design_pattern,
    suggest_patterns_for_description,
    AZURE_ARCHITECTURE_CATALOG,
    list_architecture_catalog,
    search_architecture_catalog,
    get_architecture_catalog_entry,
)
from .drawio_engine import DrawioEngine
from .visio_engine import VisioEngine
from .waf_validator import WafValidator

logger = logging.getLogger(__name__)

# ── Singleton instances ───────────────────────────────────────────

mcp = FastMCP(
    "visio-azure-mcp",
    instructions=(
        "MCP server for drawing Azure architecture diagrams in Microsoft Visio "
        "aligned with Azure Architecture Center standards and reference architectures. "
        "Supports official Azure SVG icons (no crop/flip/rotate), numbered workflow steps, "
        "Microsoft-standard boundary colors, and validation against WAF and CAF. "
        "Includes templates for: Baseline Foundry Chat, Azure Landing Zone, "
        "Baseline Web App, AI Landing Zone, and Microservices on AKS."
    ),
)

_diagram = DiagramManager()
_layout = LayoutEngine()
_waf = WafValidator()
_caf = CafValidator()


# ═══════════════════════════════════════════════════════════════════
# TOOL: create_diagram
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def create_diagram(name: str = "Azure Architecture") -> dict[str, Any]:
    """Create a new, empty Azure architecture diagram.

    Args:
        name: Title for the diagram. Appears as the Visio page name and title block.

    Returns:
        Confirmation with diagram metadata.
    """
    state = _diagram.new_diagram(name)
    return {
        "status": "created",
        "name": state.name,
        "page_size": f"{state.page_width}x{state.page_height} inches",
        "message": f"New diagram '{name}' created. Use add_azure_resource to populate it.",
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: list_azure_shapes
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def list_azure_shapes(
    category: str | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    """List available Azure resource shapes that can be added to a diagram.

    Args:
        category: Filter by category (e.g., 'Compute', 'Networking', 'Databases').
                  Pass None to list all.
        search: Search term to filter shapes by name (e.g., 'sql', 'container').

    Returns:
        List of available shapes with their keys, names, and categories.
    """
    if search:
        shapes = search_shapes(search, category)
    elif category:
        shapes = [s for s in AZURE_SHAPE_CATALOG.values() if s.category.value.lower() == category.lower()]
    else:
        shapes = list(AZURE_SHAPE_CATALOG.values())

    return {
        "count": len(shapes),
        "categories": list_categories(),
        "shapes": [
            {
                "key": s.key,
                "name": s.display_name,
                "category": s.category.value,
                "has_svg_icon": bool(s.svg_icon),
                "waf_tips": s.waf_considerations if s.waf_considerations else None,
            }
            for s in shapes
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: add_azure_resource
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def add_azure_resource(
    resource_type: str,
    display_name: str,
    resource_id: str | None = None,
    x: float = 4.0,
    y: float = 4.0,
    group_id: str | None = None,
    properties: str | None = None,
) -> dict[str, Any]:
    """Add an Azure resource shape to the current diagram.

    Args:
        resource_type: The resource type key from the shape catalog
                       (e.g., 'virtual_machine', 'app_service', 'sql_database').
                       Use list_azure_shapes to see all available types.
        display_name: Display label for this resource instance
                      (e.g., 'vm-webapp-prod-001').
        resource_id: Optional unique ID. Auto-generated if not provided.
        x: X position in inches from left edge (default: 4.0).
        y: Y position in inches from top edge (default: 4.0).
        group_id: ID of a boundary group to place this resource inside.
        properties: JSON string of additional properties
                    (e.g., '{"sku": "Standard_D2s_v3", "region": "eastus"}').

    Returns:
        The created resource details including its ID, plus any WAF considerations.
    """
    # Resolve common aliases (e.g., "aks" -> "kubernetes_service")
    resource_type = resolve_alias(resource_type)

    shape_info = AZURE_SHAPE_CATALOG.get(resource_type)
    if not shape_info:
        available = [k for k in AZURE_SHAPE_CATALOG if resource_type.lower() in k]
        return {
            "status": "error",
            "message": f"Unknown resource type '{resource_type}'.",
            "did_you_mean": available[:5] if available else "Use list_azure_shapes to see available types.",
        }

    props = {}
    if properties:
        props = json.loads(properties)

    resource = _diagram.add_resource(
        resource_type=resource_type,
        display_name=display_name,
        resource_id=resource_id,
        x=x,
        y=y,
        group_id=group_id,
        properties=props,
    )

    result: dict[str, Any] = {
        "status": "added",
        "resource": {
            "id": resource.id,
            "type": resource_type,
            "name": display_name,
            "position": {"x": resource.position.x, "y": resource.position.y},
            "group_id": resource.group_id,
        },
    }

    if shape_info.waf_considerations:
        result["waf_considerations"] = shape_info.waf_considerations

    return result


# ═══════════════════════════════════════════════════════════════════
# TOOL: add_boundary
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def add_boundary(
    boundary_type: str,
    display_name: str,
    boundary_id: str | None = None,
    x: float = 1.0,
    y: float = 1.0,
    width: float = 6.0,
    height: float = 4.0,
    parent_id: str | None = None,
    properties: str | None = None,
) -> dict[str, Any]:
    """Add a visual boundary/container to the diagram (resource group, VNet, subnet, etc.).

    Args:
        boundary_type: Type of boundary. Options: subscription, resource_group, vnet,
                       subnet, availability_zone, region, management_group, nsg.
        display_name: Display label (e.g., 'rg-app-prod-eastus').
        boundary_id: Optional unique ID. Auto-generated if not provided.
        x: X position of boundary top-left corner in inches.
        y: Y position of boundary top-left corner in inches.
        width: Width in inches (default: 6.0).
        height: Height in inches (default: 4.0).
        parent_id: ID of a parent boundary for nesting (e.g., VNet inside a resource group).
        properties: JSON string of additional properties.

    Returns:
        The created boundary details.
    """
    valid_types = set(BOUNDARY_STYLES.keys())
    if boundary_type not in valid_types:
        return {
            "status": "error",
            "message": f"Unknown boundary type '{boundary_type}'.",
            "valid_types": sorted(valid_types),
        }

    props = {}
    if properties:
        props = json.loads(properties)

    boundary = _diagram.add_boundary(
        boundary_type=boundary_type,
        display_name=display_name,
        boundary_id=boundary_id,
        x=x,
        y=y,
        width=width,
        height=height,
        parent_id=parent_id,
        properties=props,
    )

    return {
        "status": "added",
        "boundary": {
            "id": boundary.id,
            "type": boundary_type,
            "name": display_name,
            "position": {"x": boundary.position.x, "y": boundary.position.y},
            "size": {"width": boundary.size.width, "height": boundary.size.height},
            "parent_id": boundary.parent_id,
        },
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: connect_resources
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def connect_resources(
    source_id: str,
    target_id: str,
    label: str = "",
    connection_type: str = "data_flow",
    style: str = "solid",
    connection_id: str | None = None,
) -> dict[str, Any]:
    """Connect two resources with a line/arrow on the diagram.

    Args:
        source_id: ID of the source resource.
        target_id: ID of the target resource.
        label: Text label on the connector (e.g., 'HTTPS', 'SQL', 'Event').
        connection_type: Type of connection. Options:
                         data_flow, network, dependency, reference, vpn_tunnel, expressroute.
        style: Line style: solid, dashed, dotted.
        connection_id: Optional unique ID for this connection.

    Returns:
        The created connection details.
    """
    valid_types = set(CONNECTOR_STYLES.keys())
    if connection_type not in valid_types:
        return {
            "status": "error",
            "message": f"Unknown connection type '{connection_type}'.",
            "valid_types": sorted(valid_types),
        }

    try:
        conn = _diagram.add_connection(
            source_id=source_id,
            target_id=target_id,
            connection_id=connection_id,
            label=label,
            connection_type=connection_type,
            style=style,
        )
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    return {
        "status": "connected",
        "connection": {
            "id": conn.id,
            "from": conn.source_id,
            "to": conn.target_id,
            "label": conn.label,
            "type": conn.connection_type,
        },
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: assign_to_boundary
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def assign_resource_to_boundary(
    resource_id: str,
    boundary_id: str,
) -> dict[str, Any]:
    """Assign a resource to a boundary group (e.g., place a VM inside a subnet).

    Args:
        resource_id: ID of the resource to assign.
        boundary_id: ID of the boundary to assign it to.

    Returns:
        Confirmation of the assignment.
    """
    ok = _diagram.assign_to_boundary(resource_id, boundary_id)
    if not ok:
        return {
            "status": "error",
            "message": f"Could not assign resource '{resource_id}' to boundary '{boundary_id}'. Check that both IDs exist.",
        }
    return {
        "status": "assigned",
        "resource_id": resource_id,
        "boundary_id": boundary_id,
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: remove_resource
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def remove_resource(resource_id: str) -> dict[str, Any]:
    """Remove a resource from the diagram (also removes its connections).

    Args:
        resource_id: ID of the resource to remove.
    """
    ok = _diagram.remove_resource(resource_id)
    return {
        "status": "removed" if ok else "error",
        "message": f"Resource '{resource_id}' removed." if ok else f"Resource '{resource_id}' not found.",
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: remove_boundary
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def remove_boundary(boundary_id: str) -> dict[str, Any]:
    """Remove a boundary from the diagram.

    Args:
        boundary_id: ID of the boundary to remove. Resources inside will be unassigned.
    """
    ok = _diagram.remove_boundary(boundary_id)
    return {
        "status": "removed" if ok else "error",
        "message": f"Boundary '{boundary_id}' removed." if ok else f"Boundary '{boundary_id}' not found.",
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: auto_layout
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def auto_layout(strategy: str = "tiered") -> dict[str, Any]:
    """Automatically arrange all shapes on the diagram.

    Args:
        strategy: Layout strategy to use.
                  'tiered' - Arranges resources left-to-right by architectural tier
                             (ingress → gateway → compute → messaging → data → analytics).
                  'grid'   - Simple grid layout.
                  'grouped'- Groups resources by their boundary, then lays out each group.

    Returns:
        Confirmation with resource positions.
    """
    valid = {"tiered", "grid", "grouped"}
    if strategy not in valid:
        return {"status": "error", "message": f"Unknown strategy '{strategy}'.", "valid": sorted(valid)}

    # Re-use stored layout hints from reference architectures if available
    layout_hints = getattr(_diagram.state, '_layout_hints', None) or None
    boundary_hints = getattr(_diagram.state, '_boundary_hints', None) or None

    _layout.auto_layout(
        _diagram.state,
        strategy=strategy,
        layout_hints=layout_hints,
        boundary_hints=boundary_hints,
    )

    positions = {
        rid: {"x": r.position.x, "y": r.position.y}
        for rid, r in _diagram.state.resources.items()
    }
    return {
        "status": "layout_applied",
        "strategy": strategy,
        "positions": positions,
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: get_diagram_state
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_diagram_state() -> dict[str, Any]:
    """Get the full current state of the diagram.

    Returns the diagram name, all resources, connections, and boundaries
    with their current positions and properties.
    """
    return _diagram.summary()


# ═══════════════════════════════════════════════════════════════════
# TOOL: validate_waf
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def validate_waf(pillar: str | None = None) -> dict[str, Any]:
    """Validate the current architecture against the Azure Well-Architected Framework.

    Checks the diagram against all five WAF pillars:
      - Reliability: HA, failover, multi-region, availability zones
      - Security: Key Vault, NSGs, private endpoints, WAF, identity
      - Cost Optimization: autoscaling, right-sizing, tier selection
      - Operational Excellence: monitoring, CI/CD, governance
      - Performance Efficiency: caching, CDN, async patterns

    Args:
        pillar: Optional - filter to a specific pillar
                ('Reliability', 'Security', 'Cost Optimization',
                 'Operational Excellence', 'Performance Efficiency').
                Pass None to check all pillars.

    Returns:
        Validation report with score, findings, and recommendations.
    """
    report = _waf.validate(_diagram.state)

    if pillar:
        # Filter findings to a specific pillar
        try:
            target_pillar = WafPillar(pillar)
        except ValueError:
            return {
                "status": "error",
                "message": f"Unknown pillar '{pillar}'.",
                "valid_pillars": [p.value for p in WafPillar],
            }
        report.findings = [
            f for f in report.findings if f.pillar == target_pillar or f.pillar == target_pillar.value
        ]

    return {
        "framework": "WAF",
        "score": report.score,
        "summary": report.summary,
        "finding_count": len(report.findings),
        "findings": [
            {
                "severity": f.severity,
                "pillar": f.pillar.value if hasattr(f.pillar, "value") else f.pillar,
                "message": f.message,
                "recommendation": f.recommendation,
                "affected_resources": f.affected_resources,
                "page": f.page,
                "page_name": f.page_name or "",
            }
            for f in report.findings
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: validate_caf
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def validate_caf(principle: str | None = None) -> dict[str, Any]:
    """Validate the current architecture against the Azure Cloud Adoption Framework.

    Checks the diagram against CAF principles:
      - Naming Convention: resource names follow CAF abbreviation guidance
      - Resource Organization: management groups, subscriptions, resource groups
      - Network Topology: hub-spoke, subnet segmentation
      - Identity and Access: Entra ID, managed identities
      - Governance: Azure Policy, tagging strategy
      - Security Baseline: Defender for Cloud, Sentinel
      - Management: monitoring, Log Analytics

    Args:
        principle: Optional - filter to a specific principle. Pass None to check all.

    Returns:
        Validation report with score, findings, and recommendations.
    """
    report = _caf.validate(_diagram.state)

    if principle:
        report.findings = [f for f in report.findings if principle.lower() in str(f.pillar).lower()]

    return {
        "framework": "CAF",
        "score": report.score,
        "summary": report.summary,
        "finding_count": len(report.findings),
        "findings": [
            {
                "severity": f.severity,
                "principle": f.pillar.value if hasattr(f.pillar, "value") else f.pillar,
                "message": f.message,
                "recommendation": f.recommendation,
                "affected_resources": f.affected_resources,
                "page": f.page,
                "page_name": f.page_name or "",
            }
            for f in report.findings
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: save_diagram
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def save_diagram(
    output_path: str,
    format: str = "vsdx",
    stencil_dir: str | None = None,
    icons_root: str | None = None,
    auto_layout_before_save: bool = True,
    layout_strategy: str = "tiered",
) -> dict[str, Any]:
    """Save the current diagram as a Visio .vsdx or draw.io (.drawio) file.

    If Microsoft Visio is installed, uses COM automation for full-fidelity output
    with official Azure SVG icons imported directly. Otherwise, uses python-vsdx
    for basic .vsdx creation. Alternatively, choose 'drawio' format for a
    portable XML file that opens in draw.io desktop, VS Code, or diagrams.net.

    Args:
        output_path: File path for the output file
                     (e.g., 'C:/diagrams/my-architecture.vsdx').
        format: Output format — 'vsdx' (default) or 'drawio'.
        stencil_dir: Optional directory containing Azure Visio stencil files (.vssx).
                     These take priority over SVG icons if both are available.
                     Only used for 'vsdx' format.
        icons_root: Optional directory containing the Azure Public Service Icons
                    (the 'Icons' folder with category subfolders like compute/, networking/).
                    Defaults to the bundled stencils directory. Only used for 'vsdx' format.
        auto_layout_before_save: Whether to auto-layout before saving (default: True).
        layout_strategy: Layout strategy if auto-layout is enabled
                         ('tiered', 'grid', 'grouped').

    Returns:
        Save status, output path, and rendering method used.
    """
    fmt = format.lower().strip()
    if fmt not in ("vsdx", "drawio"):
        return {"status": "error", "message": f"Unsupported format '{format}'. Use 'vsdx' or 'drawio'."}

    # Resolve relative paths to a well-known output directory
    _output_dir = Path(__file__).resolve().parent.parent.parent / "output"
    out = Path(output_path)
    if not out.is_absolute():
        out = _output_dir / out.name  # always land in output/
    if not out.suffix:
        out = out.with_suffix(f".{fmt}")
    # Force correct extension for the chosen format
    expected_ext = f".{fmt}"
    if out.suffix.lower() != expected_ext:
        out = out.with_suffix(expected_ext)
    out.parent.mkdir(parents=True, exist_ok=True)
    output_path = str(out)

    if auto_layout_before_save and not _diagram.state.properties.get("preserve_original_style"):
        # Use stored layout hints if available (from reference architectures)
        layout_hints = getattr(_diagram.state, '_layout_hints', None) or None
        boundary_hints = getattr(_diagram.state, '_boundary_hints', None) or None
        if layout_hints or boundary_hints:
            _layout.auto_layout(
                _diagram.state,
                strategy=layout_strategy,
                layout_hints=layout_hints,
                boundary_hints=boundary_hints,
            )
        else:
            # Only auto-layout if resources haven't been positioned yet
            has_positioned = any(
                r.position.x > 0.1 or r.position.y > 0.1
                for r in _diagram.state.resources.values()
            )
            if not has_positioned:
                _layout.auto_layout(_diagram.state, strategy=layout_strategy)

    if fmt == "drawio":
        engine = DrawioEngine()
        rendering_method = "draw.io (mxGraph XML)"
    else:
        engine = VisioEngine(stencil_dir=stencil_dir, icons_root=icons_root)
        from .visio_engine import VISIO_AVAILABLE
        rendering_method = "Visio COM automation (SVG icons)" if VISIO_AVAILABLE else "python-vsdx (basic)"

    try:
        saved_path = engine.render(_diagram.state, output_path)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save diagram: {e}",
        }

    return {
        "status": "saved",
        "output_path": saved_path,
        "format": fmt,
        "rendering_method": rendering_method,
        "resource_count": len(_diagram.state.resources),
        "connection_count": len(_diagram.state.connections),
        "boundary_count": len(_diagram.state.boundaries),
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: get_waf_tips
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_waf_tips(resource_type: str) -> dict[str, Any]:
    """Get WAF (Well-Architected Framework) tips for a specific Azure resource type.

    Args:
        resource_type: The resource type key (e.g., 'virtual_machine', 'sql_database').

    Returns:
        WAF considerations organized by pillar for the specified resource.
    """
    shape_info = AZURE_SHAPE_CATALOG.get(resource_type)
    if not shape_info:
        return {
            "status": "error",
            "message": f"Unknown resource type '{resource_type}'.",
        }

    return {
        "resource_type": resource_type,
        "display_name": shape_info.display_name,
        "waf_considerations": shape_info.waf_considerations or {"note": "No specific WAF tips cataloged for this resource."},
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: suggest_architecture
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def suggest_architecture_improvements() -> dict[str, Any]:
    """Analyze the current diagram and suggest architectural improvements.

    Runs both WAF and CAF validations and provides a prioritized list of
    improvements with specific resources to add.

    Returns:
        Combined analysis with prioritized recommendations.
    """
    waf_report = _waf.validate(_diagram.state)
    caf_report = _caf.validate(_diagram.state)

    # Collect resources to suggest adding
    resource_types = {r.resource_type for r in _diagram.state.resources.values()}
    suggestions = []

    # Security essentials
    if "key_vault" not in resource_types:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "key_vault",
            "reason": "WAF Security + CAF Security Baseline: centralized secrets management",
            "priority": "high",
        })
    if "managed_identity" not in resource_types:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "managed_identity",
            "reason": "WAF Security + CAF Identity: passwordless service-to-service auth",
            "priority": "high",
        })

    # Monitoring essentials
    monitoring_types = {"monitor", "log_analytics", "application_insights"}
    if not (resource_types & monitoring_types):
        suggestions.append({
            "action": "add_resource",
            "resource_type": "log_analytics",
            "reason": "WAF Operational Excellence + CAF Management: centralized logging",
            "priority": "high",
        })
        suggestions.append({
            "action": "add_resource",
            "resource_type": "application_insights",
            "reason": "WAF Operational Excellence: application performance monitoring",
            "priority": "medium",
        })

    # Network security
    has_vnet = any(b.boundary_type in ("vnet", "subnet") for b in _diagram.state.boundaries.values())
    if has_vnet and "firewall" not in resource_types and "nsg" not in resource_types:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "firewall",
            "reason": "WAF Security + CAF Network Topology: centralized network security",
            "priority": "high",
        })

    # Identity
    if "entra_id" not in resource_types:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "entra_id",
            "reason": "CAF Identity: centralized identity management",
            "priority": "medium",
        })

    # Governance
    if "policy" not in resource_types and len(_diagram.state.resources) > 5:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "policy",
            "reason": "CAF Governance: enforce compliance and standards",
            "priority": "low",
        })

    # Boundary suggestions
    rg_boundaries = [b for b in _diagram.state.boundaries.values() if b.boundary_type == "resource_group"]
    if not rg_boundaries and len(_diagram.state.resources) > 2:
        suggestions.append({
            "action": "add_boundary",
            "boundary_type": "resource_group",
            "reason": "CAF Resource Organization: group resources by lifecycle",
            "priority": "medium",
        })

    return {
        "waf_score": waf_report.score,
        "caf_score": caf_report.score,
        "waf_summary": waf_report.summary,
        "caf_summary": caf_report.summary,
        "critical_issues": [
            {
                "source": f.pillar.value if hasattr(f.pillar, "value") else str(f.pillar),
                "message": f.message,
                "recommendation": f.recommendation,
            }
            for f in waf_report.findings + caf_report.findings
            if f.severity == "critical"
        ],
        "suggested_additions": suggestions,
    }


# ═══════════════════════════════════════════════════════════════════
# RESOURCES
# ═══════════════════════════════════════════════════════════════════

@mcp.resource("azure://shape-catalog")
def shape_catalog_resource() -> str:
    """Complete Azure shape catalog as a resource."""
    return json.dumps(
        {k: v.model_dump() for k, v in AZURE_SHAPE_CATALOG.items()},
        indent=2,
    )


@mcp.resource("azure://connector-styles")
def connector_styles_resource() -> str:
    """Available connector/line styles."""
    return json.dumps(CONNECTOR_STYLES, indent=2)


@mcp.resource("azure://boundary-styles")
def boundary_styles_resource() -> str:
    """Available boundary/container styles."""
    return json.dumps(BOUNDARY_STYLES, indent=2)


@mcp.resource("azure://reference-architectures")
def reference_architectures_resource() -> str:
    """Available Azure Architecture Center reference architecture templates."""
    return json.dumps(list_reference_architectures(), indent=2)


@mcp.resource("azure://diagram-standards")
def diagram_standards_resource() -> str:
    """Microsoft Azure Architecture Center diagram visual standards."""
    return json.dumps({
        "colors": AZURE_DIAGRAM_COLORS,
        "icon_guidelines": {
            "do": [
                "Use official Azure SVG icons at 1:1 aspect ratio",
                "Include product name label adjacent to every icon",
                "Use icons as they would appear within Azure",
            ],
            "dont": [
                "Don't crop, flip, or rotate icons",
                "Don't distort or change icon shape in any way",
                "Don't use Microsoft product icons to represent your product or service",
            ],
        },
        "layout_conventions": {
            "flow_direction": "Top-to-bottom (TB) or left-to-right (LR)",
            "workflow_steps": "Numbered circles on data-flow arrows",
            "boundaries": "Gray for RGs, light blue for VNet, light green for subnets, dashed borders for VNet/subnet",
            "connectors": "Solid for data flow, dashed for management/identity, dotted for private links",
        },
        "source": "https://learn.microsoft.com/en-us/azure/architecture/icons/",
    }, indent=2)


@mcp.resource("azure://architecture-styles")
def architecture_styles_resource() -> str:
    """Azure Architecture Center architecture styles — N-Tier, Microservices, Event-Driven, etc."""
    return json.dumps(list_architecture_styles(), indent=2)


# ═══════════════════════════════════════════════════════════════════
# TOOLS: Architecture Style Guidance
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def suggest_architecture_style(description: str) -> dict[str, Any]:
    """Suggest the best-fit Azure architecture style for a workload description.

    Analyzes the description against 14 architecture styles from
    the Azure Architecture Center including N-Tier, Web-Queue-Worker, Microservices,
    Event-Driven, Big Data, Big Compute (HPC), Dataflow, Big Data Analytics,
    Database Flow, AI/ML Pipeline, RAG AI App, Streaming Analytics, and more.

    Returns ranked suggestions with typical components, recommended Azure
    services, and diagram layout conventions for each style.

    Args:
        description: Natural language description of the workload or scenario
                     (e.g., "real-time IoT data processing pipeline").

    Returns:
        Ranked list of architecture styles with guidance on Azure services
        and diagram conventions.
    """
    suggestions = suggest_style_for_description(description)
    if not suggestions:
        return {
            "message": "No strong match found. Provide more detail about the workload.",
            "all_styles": [s["name"] for s in list_architecture_styles()],
        }
    return {
        "count": len(suggestions),
        "suggestions": suggestions,
    }


@mcp.tool()
def get_architecture_style_detail(style_key: str) -> dict[str, Any]:
    """Get detailed information about a specific architecture style.

    Returns full details including when to use it, typical components,
    recommended Azure services, and diagram layout conventions.

    Args:
        style_key: Architecture style key — e.g., n_tier, web_queue_worker,
                   microservices, event_driven, big_data, big_compute,
                   dataflow, big_data_analytics, database_flow, ai_ml_pipeline.

    Returns:
        Complete architecture style details or error if not found.
    """
    style = get_architecture_style(style_key)
    if not style:
        return {
            "error": f"Unknown style '{style_key}'",
            "available": [s["key"] for s in list_architecture_styles()],
        }
    return {
        "key": style.key,
        "name": style.name,
        "description": style.description,
        "source_url": style.source_url,
        "when_to_use": style.when_to_use,
        "typical_components": style.typical_components,
        "azure_services": style.azure_services,
        "flow_direction": style.flow_direction,
        "layout_strategy": style.layout_strategy,
        "diagram_conventions": style.diagram_conventions,
    }


# ═══════════════════════════════════════════════════════════════════
# RESOURCE: Cloud Design Patterns
# ═══════════════════════════════════════════════════════════════════

@mcp.resource("azure://design-patterns")
def design_patterns_resource() -> str:
    """Azure Architecture Center cloud design patterns — CQRS, Event Sourcing, Saga, etc."""
    return json.dumps(list_design_patterns(), indent=2)


# ═══════════════════════════════════════════════════════════════════
# TOOLS: Cloud Design Pattern Guidance
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def suggest_design_patterns(description: str) -> dict[str, Any]:
    """Suggest cloud design patterns for a workload challenge or scenario.

    Analyzes the description against 50 cloud design patterns from the
    Azure Architecture Center (e.g., CQRS, Event Sourcing, Saga, Circuit
    Breaker, Cache-Aside, Publisher-Subscriber, Strangler Fig, Data Lake,
    ETL/ELT, Lambda Architecture, MLOps CI/CD, RAG, etc.).

    Returns ranked suggestions with WAF pillar alignment, Azure services,
    related patterns, and diagram layout implications.

    Args:
        description: Natural language description of the challenge or scenario
                     (e.g., "handle distributed transactions across microservices",
                     "migrate a legacy monolith to Azure incrementally").

    Returns:
        Ranked list of design patterns with guidance.
    """
    suggestions = suggest_patterns_for_description(description)
    if not suggestions:
        return {
            "message": "No strong match found. Provide more detail about the challenge.",
            "all_patterns": [p["name"] for p in list_design_patterns()],
        }
    return {
        "count": len(suggestions),
        "suggestions": suggestions,
    }


@mcp.tool()
def get_design_pattern_detail(pattern_key: str) -> dict[str, Any]:
    """Get detailed information about a specific cloud design pattern.

    Returns full details including when to use it, when not to use it,
    WAF pillar alignment, Azure services, related patterns, and
    diagram layout implications.

    Args:
        pattern_key: Design pattern key — e.g., cqrs, event_sourcing, saga,
                     circuit_breaker, cache_aside, publisher_subscriber,
                     strangler_fig, sidecar, retry, bulkhead, etc.

    Returns:
        Complete design pattern details or error if not found.
    """
    pattern = get_design_pattern(pattern_key)
    if not pattern:
        return {
            "error": f"Unknown pattern '{pattern_key}'",
            "available": [p["key"] for p in list_design_patterns()],
        }
    return {
        "key": pattern.key,
        "name": pattern.name,
        "description": pattern.description,
        "source_url": pattern.source_url,
        "waf_pillars": pattern.waf_pillars,
        "when_to_use": pattern.when_to_use,
        "when_not_to_use": pattern.when_not_to_use,
        "related_patterns": pattern.related_patterns,
        "azure_services": pattern.azure_services,
        "diagram_implications": pattern.diagram_implications,
    }


# ═══════════════════════════════════════════════════════════════════
# TOOLS & RESOURCES: Azure Architecture Catalog (206 entries)
# ═══════════════════════════════════════════════════════════════════

@mcp.resource("azure://architecture-catalog")
def architecture_catalog_resource() -> str:
    """Full Azure Architecture Catalog — 206 reference architectures and solution ideas from Azure Architecture Center."""
    entries = []
    for entry in AZURE_ARCHITECTURE_CATALOG.values():
        entries.append({
            "key": entry.key,
            "name": entry.name,
            "type": entry.entry_type,
            "categories": entry.categories,
            "source_url": entry.source_url,
        })
    return json.dumps(entries, indent=2)


@mcp.tool()
def browse_architecture_catalog(
    category: str | None = None,
    entry_type: str | None = None,
) -> dict[str, Any]:
    """Browse the Azure Architecture Catalog (206 architectures & solutions).

    Filter by category (e.g. 'AI + Machine Learning', 'Networking', 'Security')
    and/or type ('Architecture', 'Reference Architecture', 'Solution Idea', 'Best Practice').

    Categories: AI + Machine Learning, Analytics, Compute, Containers, Databases,
    DevOps, Developer Tools, Hybrid + Multicloud, Identity, Integration,
    Internet of Things, Media, Migration, Networking, Security, Storage, Web.
    """
    results = list_architecture_catalog(
        category=category or "",
        entry_type=entry_type or "",
    )
    return {
        "count": len(results),
        "filters": {"category": category, "type": entry_type},
        "entries": results,
    }


@mcp.tool()
def search_arch_catalog(query: str) -> dict[str, Any]:
    """Search the Azure Architecture Catalog by keyword.

    Searches across names, summaries, categories, and Azure products.
    Returns up to 15 ranked results.
    """
    results = search_architecture_catalog(query)
    return {
        "query": query,
        "count": len(results),
        "results": results,
    }


@mcp.tool()
def get_arch_catalog_entry(key: str) -> dict[str, Any]:
    """Get full details for a specific Azure Architecture Catalog entry.

    Use browse_architecture_catalog or search_arch_catalog to find keys first.
    """
    entry = get_architecture_catalog_entry(key)
    if entry is None:
        return {"error": f"Architecture catalog entry '{key}' not found"}
    return entry


# ═══════════════════════════════════════════════════════════════════
# TOOLS: Reference Architecture
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def list_reference_archs(category: str | None = None) -> dict[str, Any]:
    """List available Azure Architecture Center reference architecture templates.

    These are official Microsoft patterns that define the standard resources,
    connections, and boundaries for common Azure workloads.

    Args:
        category: Optional filter by category (e.g., 'AI + Machine Learning',
                  'Web', 'Containers', 'Management + Governance').

    Returns:
        List of available reference architectures with keys, names, and descriptions.
    """
    archs = list_reference_architectures()
    if category:
        cat_lower = category.lower()
        archs = [a for a in archs if cat_lower in a["category"].lower()]
    return {"count": len(archs), "reference_architectures": archs}


@mcp.tool()
def apply_reference_architecture(
    architecture_key: str,
    name_override: str | None = None,
    merge: bool = False,
) -> dict[str, Any]:
    """Create or extend a diagram from an Azure Architecture Center reference architecture template.

    Builds the complete architecture with all standard resources, connections,
    boundaries, and workflow steps per Microsoft's published patterns.

    When merge=False (default), creates a new diagram replacing any existing state.
    When merge=True, adds the reference architecture's resources, boundaries, and
    connections INTO the existing diagram without clearing it. Use merge=True when
    the user already has a diagram and wants to add/combine another architecture.

    Available keys:
      - baseline_foundry_chat  (Baseline E2E Chat with Foundry)
      - azure_landing_zone     (CAF Landing Zone with Hub-Spoke)
      - baseline_web_app       (Baseline Zone-Redundant Web App)
      - ai_landing_zone        (AI Workload in Azure Landing Zone)
      - microservices_aks      (Microservices on AKS)

    Args:
        architecture_key: Key of the reference architecture template.
        name_override: Optional custom name for the diagram.
        merge: If True, merge into the existing diagram instead of creating a new one.

    Returns:
        Summary of created resources, connections, boundaries, and workflow steps.
    """
    arch = get_reference_architecture(architecture_key)
    if arch is None:
        available = [k for k in REFERENCE_ARCHITECTURES]
        return {
            "status": "error",
            "message": f"Unknown architecture key '{architecture_key}'. Available: {available}",
        }

    # Create fresh diagram or merge into existing
    diagram_name = name_override or arch.name
    existing_counts = {"resources": 0, "connections": 0, "boundaries": 0}
    if merge and _diagram.state.resources:
        # Keep existing state, just append new items
        existing_counts = {
            "resources": len(_diagram.state.resources),
            "connections": len(_diagram.state.connections),
            "boundaries": len(_diagram.state.boundaries),
        }
        # Optionally update diagram name to reflect combined architecture
        if name_override:
            _diagram.state.name = name_override
    else:
        _diagram.new_diagram(diagram_name)

    # Create boundaries (skip existing when merging)
    boundary_count = 0
    for bt in arch.boundaries:
        if merge and bt.boundary_id in _diagram.state.boundaries:
            continue
        _diagram.add_boundary(
            boundary_type=bt.boundary_type,
            display_name=bt.display_name,
            boundary_id=bt.boundary_id,
            parent_id=bt.parent_id,
        )
        boundary_count += 1

    # Create resources (skip existing when merging, auto-generate caf_name for CAF validation)
    resource_count = 0
    for rt in arch.resources:
        if merge and rt.resource_id in _diagram.state.resources:
            continue
        props = dict(rt.properties) if rt.properties else {}
        if "caf_name" not in props:
            prefix = CAF_NAMING_PREFIXES.get(rt.resource_type, "")
            if prefix:
                props["caf_name"] = f"{prefix}{diagram_name.lower().replace(' ', '-')}-prod-eastus"
        _diagram.add_resource(
            resource_type=rt.resource_type,
            display_name=rt.display_name,
            resource_id=rt.resource_id,
            group_id=rt.group_id or None,
            properties=props,
        )
        resource_count += 1

    # Create connections (skip any that reference boundary IDs rather than resources)
    connection_count = 0
    skipped_connections = 0
    boundary_ids = {bt.boundary_id for bt in arch.boundaries}
    for ct in arch.connections:
        if ct.source_id in boundary_ids or ct.target_id in boundary_ids:
            skipped_connections += 1
            continue
        label = ct.label
        if ct.workflow_step:
            label = f"({ct.workflow_step}) {ct.label}"
        try:
            _diagram.add_connection(
                source_id=ct.source_id,
                target_id=ct.target_id,
                label=label,
                connection_type=ct.connection_type,
            )
            connection_count += 1
        except ValueError:
            skipped_connections += 1

    # Store hints on the diagram state (so auto_layout tool can re-use them)
    if arch.layout_hints:
        if merge and hasattr(_diagram.state, "_layout_hints") and _diagram.state._layout_hints:
            _diagram.state._layout_hints.update(dict(arch.layout_hints))
        else:
            _diagram.state._layout_hints = dict(arch.layout_hints)
    if arch.boundary_hints:
        if merge and hasattr(_diagram.state, "_boundary_hints") and _diagram.state._boundary_hints:
            _diagram.state._boundary_hints.update(dict(arch.boundary_hints))
        else:
            _diagram.state._boundary_hints = dict(arch.boundary_hints)

    # Collect all hints for layout
    all_layout_hints = getattr(_diagram.state, "_layout_hints", None)
    all_boundary_hints = getattr(_diagram.state, "_boundary_hints", None)

    # Auto-layout (use position hints from reference architecture if available)
    _layout.auto_layout(
        _diagram.state,
        strategy=arch.layout_strategy,
        layout_hints=all_layout_hints,
        boundary_hints=all_boundary_hints,
    )

    result = {
        "status": "merged" if merge else "created",
        "name": _diagram.state.name,
        "source_url": arch.source_url,
        "resource_count": resource_count,
        "connection_count": connection_count,
        "boundary_count": boundary_count,
        "workflow_steps": [
            {"step": ws.number, "description": ws.description}
            for ws in arch.workflow_steps
        ],
        "waf_notes": arch.waf_notes,
        "caf_notes": arch.caf_notes,
        "flow_direction": arch.flow_direction,
    }
    if merge:
        result["total_resources"] = len(_diagram.state.resources)
        result["total_connections"] = len(_diagram.state.connections)
        result["total_boundaries"] = len(_diagram.state.boundaries)
        result["existing_before_merge"] = existing_counts
    return result


@mcp.tool()
def get_reference_arch_details(architecture_key: str) -> dict[str, Any]:
    """Get detailed information about a reference architecture template.

    Returns all resources, connections, boundaries, workflow steps,
    and WAF/CAF alignment notes for the specified architecture.

    Args:
        architecture_key: Key of the reference architecture template.

    Returns:
        Complete template details including all components and Microsoft guidance.
    """
    arch = get_reference_architecture(architecture_key)
    if arch is None:
        available = [k for k in REFERENCE_ARCHITECTURES]
        return {
            "status": "error",
            "message": f"Unknown architecture key '{architecture_key}'. Available: {available}",
        }

    return {
        "name": arch.name,
        "description": arch.description,
        "source_url": arch.source_url,
        "category": arch.category,
        "flow_direction": arch.flow_direction,
        "layout_strategy": arch.layout_strategy,
        "boundaries": [
            {"id": b.boundary_id, "type": b.boundary_type, "name": b.display_name, "parent": b.parent_id}
            for b in arch.boundaries
        ],
        "resources": [
            {"id": r.resource_id, "type": r.resource_type, "name": r.display_name, "group": r.group_id}
            for r in arch.resources
        ],
        "connections": [
            {"source": c.source_id, "target": c.target_id, "label": c.label,
             "type": c.connection_type, "workflow_step": c.workflow_step}
            for c in arch.connections
        ],
        "workflow_steps": [
            {"step": ws.number, "description": ws.description}
            for ws in arch.workflow_steps
        ],
        "waf_notes": arch.waf_notes,
        "caf_notes": arch.caf_notes,
    }


@mcp.tool()
def get_diagram_standards() -> dict[str, Any]:
    """Get Microsoft Azure Architecture Center diagram visual standards.

    Returns the official color palette, icon guidelines, layout conventions,
    and connector styling rules that should be followed when creating diagrams.

    Returns:
        Complete visual standards per Azure Architecture Center.
    """
    return {
        "colors": AZURE_DIAGRAM_COLORS,
        "icon_guidelines": {
            "do": [
                "Use official Azure SVG icons at 1:1 aspect ratio",
                "Include product name label adjacent to every icon",
                "Use icons as they would appear within Azure",
            ],
            "dont": [
                "Don't crop, flip, or rotate icons",
                "Don't distort or change icon shape in any way",
                "Don't use Microsoft product icons to represent your product or service",
            ],
            "source": "https://learn.microsoft.com/en-us/azure/architecture/icons/",
        },
        "boundary_colors": {
            "subscription": "#E5E5E5 (light gray)",
            "resource_group": "#F2F2F2 (near-white gray)",
            "vnet": "#DEEAF6 (light blue, dashed border)",
            "subnet": "#E2F0D9 (light green, dashed border)",
            "management_group": "#E8E0EE (light purple)",
            "security_zone": "#FCE4EC (light pink)",
        },
        "connector_styles": {
            "data_flow": "Solid blue (#0078D4) — primary data movement",
            "dependency": "Dashed gray (#666666) — management/identity/config",
            "network": "Solid green (#107C10) — network routing",
            "private_link": "Dotted red (#E74856) — private endpoint connections",
            "identity": "Dashed gold (#FFB900) — authentication flows",
        },
        "layout_rules": {
            "flow": "Top-to-bottom or left-to-right",
            "workflow_steps": "Numbered blue circles on data-flow arrows",
            "grouping": "Resources inside VNet > Subnet > Resource Group boundaries",
            "private_endpoints": "Show as explicit shapes in dedicated PE subnet",
            "external_actors": "Users/Internet/On-prem outside all boundaries (top or left)",
        },
    }


# ═══════════════════════════════════════════════════════════════════
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
# PROMPTS
# ═══════════════════════════════════════════════════════════════════

@mcp.prompt()
def getting_started() -> str:
    """How-to guide for first-time users of the Azure Visio MCP server."""
    return """# Getting Started with Azure Visio MCP Server

## Quick Start (3 steps)

1. **Create a diagram** — call `create_diagram` with a name, e.g.:
   `create_diagram(name="My Azure Architecture")`

2. **Add resources** — use `add_azure_resource` with a shape key from the catalog:
   `add_azure_resource(resource_type="app_service", display_name="Web App")`
   Use `list_azure_shapes()` to see all 151 available Azure resource types.

3. **Save** — call `save_diagram` with a path and format:
   `save_diagram(output_path="diagram.vsdx", format="vsdx")`
   Supported formats: `vsdx` (Microsoft Visio) or `drawio` (draw.io XML).

## Common Workflows

### Build from a reference architecture template
```
list_reference_archs()                        # See 5 available templates
apply_reference_architecture("baseline_web_app")  # Creates full diagram
```
Templates: baseline_foundry_chat, azure_landing_zone, baseline_web_app, ai_landing_zone, microservices_aks

### Add resources and connect them
```
add_azure_resource(resource_type="app_service", display_name="web-app-prod")
add_azure_resource(resource_type="sql_database", display_name="sqldb-prod")
connect_resources(source_id="web-app-prod", target_id="sqldb-prod", label="SQL")
```

### Group resources inside boundaries
```
add_boundary(boundary_type="virtual_network", display_name="vnet-prod")
add_azure_resource(resource_type="app_service", display_name="app-01", group_id="vnet-prod")
```

### Validate architecture quality
```
validate_waf()   # Well-Architected Framework (6 pillars: Reliability, Security, Cost, etc.)
validate_caf()   # Cloud Adoption Framework (naming, tagging, structure)
```

### Browse the architecture catalog (206 entries)
```
browse_architecture_catalog(category="AI + Machine Learning")
search_arch_catalog(query="kubernetes")
```

## Available Resources (read with resources/read)
- `azure://shape-catalog` — All 151 Azure shapes with icons & WAF tips
- `azure://reference-architectures` — 5 buildable architecture templates
- `azure://architecture-catalog` — 206 Architecture Center entries
- `azure://architecture-styles` — 6 architecture styles (microservices, event-driven, etc.)
- `azure://design-patterns` — 40 cloud design patterns
- `azure://connector-styles` — Connection line types and styles
- `azure://boundary-styles` — Boundary grouping types (VNet, subnet, etc.)
- `azure://diagram-standards` — Microsoft visual standards and color palette

## 28 Tools Summary
| Tool | Purpose |
|------|---------|
| create_diagram | Create new empty diagram |
| list_azure_shapes | Browse 151 Azure resource types |
| add_azure_resource | Place a resource on the diagram |
| add_boundary | Add a grouping boundary (VNet, subnet, RG, etc.) |
| connect_resources | Connect two resources with a line/arrow |
| assign_resource_to_boundary | Move a resource into a boundary |
| remove_resource / remove_boundary | Remove elements |
| auto_layout | Auto-arrange the diagram layout |
| get_diagram_state | Get current diagram contents |
| save_diagram | Save as .vsdx or .drawio |
| validate_waf / validate_caf | Architecture validation |
| get_waf_tips | WAF tips for a specific resource type |
| suggest_architecture_improvements | AI-powered improvement suggestions |
| list_reference_archs | List 16 reference architecture templates |
| apply_reference_architecture | Build a full diagram from a template |
| suggest_architecture_style | Recommend a style for your workload |
| suggest_design_patterns | Recommend design patterns |
| browse_architecture_catalog | Browse 206 Architecture Center entries |
| search_arch_catalog | Search the catalog by keyword |
| import_vsdx | Import an existing Visio file |
| import_image | Convert an image/screenshot to a diagram |
"""


@mcp.prompt()
def hub_spoke_architecture() -> str:
    """Prompt template for Azure Landing Zone hub-spoke architecture per Azure Architecture Center."""
    return """Create an Azure hub-spoke architecture aligned with the Azure Architecture Center
landing zone reference architecture.

Use `apply_reference_architecture("azure_landing_zone")` to start from the official template,
or build manually following these Microsoft standards:

1. Management Group hierarchy (per CAF):
   - Root MG → Platform MG (Identity, Management, Connectivity subscriptions)
   - Root MG → Landing Zones MG (Corp, Online sub-groups)

2. Hub VNet (Connectivity subscription):
   - AzureFirewallSubnet with Azure Firewall Premium
   - GatewaySubnet with VPN Gateway / ExpressRoute
   - AzureBastionSubnet with Azure Bastion
   - snet-dns-inbound for Private DNS

3. Spoke VNets (one per workload landing zone):
   - Peered to Hub, forced tunneling through Firewall
   - Dedicated subnets per function (compute, PE, integration)

4. Platform shared services (Management subscription):
   - Log Analytics, Azure Monitor, Azure Policy
   - Defender for Cloud, Microsoft Sentinel

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/

Validate with WAF and CAF after creation."""


@mcp.prompt()
def three_tier_web_app() -> str:
    """Prompt template for baseline zone-redundant web app per Azure Architecture Center."""
    return """Create a baseline zone-redundant web application architecture aligned
with the Azure Architecture Center reference pattern.

Use `apply_reference_architecture("baseline_web_app")` to start from the official template,
or build manually following these Microsoft standards:

1. Ingress (snet-appGateway subnet):
   - Application Gateway with WAF v2 in Prevention mode
   - DDoS Protection Plan on public IP

2. Compute (snet-appServiceIntegration subnet):
   - App Service with VNet integration, zone-redundant P1v3
   - Deployment slots for zero-downtime deploys

3. Private endpoint subnet (snet-privateEndpoints):
   - PE: SQL Database, PE: Key Vault, PE: Storage
   - All PaaS accessed only through private endpoints

4. Data tier (separate resource group):
   - Azure SQL Database (BusinessCritical, zone-redundant)
   - Azure Storage (ZRS)

5. Shared services (separate resource group):
   - Key Vault, Managed Identity, Entra ID
   - Application Insights + Log Analytics

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service/architectures/baseline-zone-redundant

Validate with WAF and CAF after creation."""


@mcp.prompt()
def microservices_architecture() -> str:
    """Prompt template for microservices on AKS per Azure Architecture Center."""
    return """Create a microservices architecture on AKS aligned with the
Azure Architecture Center reference pattern.

Use `apply_reference_architecture("microservices_aks")` to start from the official template,
or build manually following these Microsoft standards:

1. Global ingress:
   - Azure Front Door for global load balancing
   - Application Gateway with AGIC for regional ingress

2. Compute (snet-aks-nodes subnet):
   - AKS private cluster (Standard SKU)
   - System + user node pools across availability zones
   - Workload Identity for pod authentication

3. Container Registry (private endpoint):
   - Image pull via private endpoint in PE subnet

4. Per-service databases (private endpoints):
   - Cosmos DB for Service A
   - Azure SQL for Service B
   - Redis Cache for shared caching

5. Async messaging:
   - Service Bus for inter-service communication
   - Event Grid for event-driven patterns

6. Observability:
   - Container Insights + Application Insights
   - Log Analytics workspace + Azure Monitor

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices

Validate with WAF and CAF after creation."""


@mcp.prompt()
def ai_chat_architecture() -> str:
    """Prompt template for baseline AI/Foundry chat per Azure Architecture Center."""
    return """Create a baseline end-to-end AI chat architecture aligned with the
Azure Architecture Center Foundry reference pattern.

Use `apply_reference_architecture("baseline_foundry_chat")` to start from the official template,
or build manually following these Microsoft standards:

1. Ingress (snet-appGateway subnet):
   - Application Gateway with WAF v2
   - DDoS Protection Plan

2. App tier (snet-appServicePlan subnet):
   - App Service (Chat UI) with VNet integration
   - Zone-redundant P1v3 plan

3. AI tier:
   - Foundry Agent Service (prompt-based agent)
   - Azure OpenAI (GPT-4o, data-zone provisioned)
   - Azure AI Search (Standard, 3 replicas)
   - snet-foundryIntegration and snet-agentsEgress subnets

4. Data tier:
   - Cosmos DB (NoSQL, continuous backup, zone-redundant)
   - Azure Storage (ZRS)

5. Network security:
   - Private endpoints for ALL PaaS services in snet-privateEndpoints
   - Azure Firewall for egress control
   - Azure Bastion + jump box for portal access
   - Private DNS Zones, NSGs per subnet

6. Shared services:
   - Key Vault, Managed Identities (per App + per Foundry project)
   - Entra ID, Log Analytics, Application Insights
   - Defender for Cloud

Workflow steps (numbered on diagram):
  1. User → App Gateway (WAF) → App Service
  2. App Service → Foundry Agent (via private endpoint)
  3. Agent processes request per system prompt
  4. Agent → AI Search (RAG retrieval)
  5. Agent → Azure Firewall (external tool calls)
  6. Agent → OpenAI model (inference)
  7. Agent → Cosmos DB (persist conversation)

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat

Validate with WAF and CAF after creation."""


@mcp.prompt()
def ai_landing_zone_architecture() -> str:
    """Prompt template for AI workload in Azure Landing Zone per CAF guidance."""
    return """Create an AI workload deployed within the Azure Landing Zone architecture,
following Microsoft CAF guidance that 'AI is just another workload — no separate
AI landing zone is needed.'

Use `apply_reference_architecture("ai_landing_zone")` to start from the official template,
or build manually following these Microsoft standards:

1. Platform Landing Zone (shared):
   - Connectivity sub: Hub VNet with Azure Firewall, VPN Gateway
   - Management sub: Log Analytics, Azure Policy, Defender, Sentinel

2. Application Landing Zone (AI workload under Corp MG):
   - Spoke VNet peered to Hub, forced tunneling through Firewall
   - snet-appGateway: Application Gateway + WAF v2
   - snet-compute: Container Apps (inference API), App Service (Chat UI)
   - snet-privateEndpoints: PEs for OpenAI, AI Search, Cosmos DB, Storage
   - snet-foundryIntegration: Foundry agent delegation

3. AI Services (rg-ai-services):
   - Azure OpenAI, AI Search (3 replicas), Azure AI Services
   - ML Workspace, Container Registry

4. Data (rg-ai-data):
   - Cosmos DB (zone-redundant, continuous backup)
   - Storage Account (GRS), Redis Cache

5. Shared (rg-ai-shared):
   - Key Vault, Managed Identity, Entra ID
   - Log Analytics (workload) → feeds Platform Log Analytics
   - Application Insights, Azure Monitor

6. Governance:
   - Azure Policy at Management Group scope
   - Defender for Cloud monitoring across subscriptions
   - Sentinel SIEM integration

Visual standards: Use `get_diagram_standards()` for Microsoft color palette and conventions.
Source: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/

Validate with WAF and CAF after creation."""


@mcp.prompt()
def business_to_architecture() -> str:
    """Translate a business case or business requirement into an Azure architecture diagram — analyze workload characteristics, select architecture style, build resources, and validate."""
    return """\
You are an Azure Solutions Architect. The user will describe a **business case** or \
**business requirement** (not a technical architecture). Your job is to translate their \
business needs into an Azure architecture diagram.

Follow this structured workflow:

## 1. Analyse the Business Requirement
Break the requirement into these dimensions:
- **Workload type** — Web app, API, batch processing, real-time analytics, AI/ML, IoT, etc.
- **Users & scale** — Expected concurrent users, requests/sec, data volume, growth trajectory
- **Data requirements** — Relational, NoSQL, files/blobs, search, caching, data lake
- **Integration** — Third-party APIs, on-premises connectivity, messaging/events
- **Security & compliance** — Authentication (B2C, B2B, internal), regulatory (PCI, HIPAA, SOC2), data residency
- **Availability & DR** — SLA target, RPO/RTO, multi-region needs
- **Budget sensitivity** — Cost-optimised vs. performance-first

## 2. Select Architecture Style
Use `suggest_architecture_style` with a description of the workload to pick the best-fit \
pattern (N-Tier, Web-Queue-Worker, Microservices, Event-Driven, Big Data, Big Compute). \
Use `get_architecture_style_detail` for deeper guidance.

## 3. Check the Architecture Catalog
Use `search_arch_catalog` with keywords from the business domain to find matching reference \
architectures or solution ideas from the 206-entry Azure Architecture Center catalog. \
If a good match exists, prefer using `apply_reference_architecture` or the catalog entry \
as a blueprint.

## 4. Identify Design Patterns
Use `suggest_design_patterns` for any cross-cutting concerns (caching, resilience, \
async processing, CQRS, etc.). Apply the returned diagram_implications when placing resources.

## 5. Build the Diagram Step-by-Step
1. `create_diagram` with a descriptive name derived from the business case
2. Add **boundaries** first (resource groups, VNets, subnets) using CAF naming: \
   `rg-<app>-<env>-<region>`, `vnet-<app>-<env>-<region>`
3. Add **resources** one by one inside boundaries, choosing the right Azure service \
   for each requirement (e.g., App Service for web, Azure SQL for relational data, \
   Redis Cache for caching, Service Bus for messaging)
4. Add **connections** with descriptive labels (e.g., "HTTPS", "Private Endpoint", \
   "Service Bus Queue")
5. `auto_layout` for clean arrangement

## 6. Validate & Iterate
Run `validate_waf` and `validate_caf` to check compliance. Fix any findings, \
then re-validate until scores are acceptable.

## 7. Explain Your Decisions
After building, provide a brief summary:
- Why you chose each Azure service
- Key architecture decisions and trade-offs
- Estimated cost tier (Dev/Test, Production, Enterprise)
- Recommendations for next steps (monitoring, CI/CD, disaster recovery)

**Important rules:**
- Always explain your reasoning *before* making tool calls
- Use CAF-compliant naming conventions throughout
- Prefer managed PaaS services over IaaS unless the requirement demands it
- Include security (NSGs, Private Endpoints, Managed Identity) by default
- Add monitoring (Application Insights, Log Analytics) unless explicitly out of scope"""


# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
