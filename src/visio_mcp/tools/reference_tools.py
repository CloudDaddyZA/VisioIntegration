"""Reference architecture tools."""

from __future__ import annotations

import json
import logging
from typing import Any

from visio_mcp._state import mcp, _diagram, _layout, _waf, _caf
from visio_mcp.azure_catalog import AZURE_SHAPE_CATALOG
from visio_mcp.caf_validator import CAF_NAMING_PREFIXES
from visio_mcp.reference_architectures import (
    AZURE_DIAGRAM_COLORS,
    REFERENCE_ARCHITECTURES,
    get_reference_architecture,
    list_reference_architectures,
    search_reference_architectures,
)
from visio_mcp.models import WafPillar

logger = logging.getLogger(__name__)

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
