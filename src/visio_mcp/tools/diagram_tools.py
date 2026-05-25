"""Diagram CRUD tools — create, add, remove, layout, get state."""

from __future__ import annotations

import json
import logging
from typing import Any

from visio_mcp._state import mcp, _diagram, _layout, _waf, _caf
from visio_mcp.azure_catalog import (
    AZURE_SHAPE_CATALOG,
    BOUNDARY_STYLES,
    CONNECTOR_STYLES,
    list_categories,
    resolve_alias,
    search_shapes,
)
from visio_mcp.layout_engine import LayoutEngine
from visio_mcp.models import WafPillar

logger = logging.getLogger(__name__)

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
    properties: str | dict | None = None,
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
        props = json.loads(properties) if isinstance(properties, str) else properties

    # Auto-position within boundary if group_id is specified and using default coords
    if group_id and group_id in _diagram.state.boundaries and x == 4.0 and y == 4.0:
        boundary = _diagram.state.boundaries[group_id]
        # Count existing resources in this boundary
        siblings = [
            r for r in _diagram.state.resources.values() if r.group_id == group_id
        ]
        padding = 0.5
        header = 0.4
        slot = len(siblings)
        # Arrange in a grid within the boundary (max 3 columns)
        cols = min(3, max(1, int(boundary.size.width / 2.0)))
        col = slot % cols
        row = slot // cols
        x = boundary.position.x + padding + 1.0 + col * 2.0
        y = boundary.position.y + padding + header + 1.0 + row * 1.5

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
    properties: str | dict | None = None,
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
        props = json.loads(properties) if isinstance(properties, str) else properties

    # Auto-position nested boundaries within parent if using defaults
    if parent_id and parent_id in _diagram.state.boundaries and x == 1.0 and y == 1.0:
        parent = _diagram.state.boundaries[parent_id]
        # Count existing child boundaries
        siblings = [
            b for b in _diagram.state.boundaries.values() if b.parent_id == parent_id
        ]
        padding = 0.5
        header = 0.5
        slot = len(siblings)
        # Stack children vertically within parent
        child_height = min(height, (parent.size.height - header - padding * 2) / max(1, slot + 1))
        x = parent.position.x + padding
        y = parent.position.y + header + slot * (child_height + 0.3)
        width = parent.size.width - padding * 2
        height = child_height

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
                             If most resources have boundary assignments, automatically
                             uses a hybrid approach that preserves grouping.
                  'grid'   - Simple grid layout.
                  'grouped'- Groups resources by their boundary, then lays out each group
                             in a grid (max 3 columns). Best when boundaries have been
                             manually structured to match a reference architecture.

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


@mcp.tool()
def get_diagram_state() -> dict[str, Any]:
    """Get the full current state of the diagram.

    Returns the diagram name, all resources, connections, and boundaries
    with their current positions and properties.
    """
    return _diagram.summary()


