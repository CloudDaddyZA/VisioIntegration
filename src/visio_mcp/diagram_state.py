"""In-memory diagram state management."""

from __future__ import annotations

import uuid

from .models import (
    BoundaryGroup,
    Connection,
    DiagramResource,
    DiagramState,
    Position,
    Size,
)


class DiagramManager:
    """Manages the current diagram state in memory."""

    def __init__(self) -> None:
        self._state = DiagramState()

    @property
    def state(self) -> DiagramState:
        return self._state

    def new_diagram(self, name: str = "Azure Architecture") -> DiagramState:
        """Create a fresh diagram, discarding any existing state."""
        self._state = DiagramState(name=name)
        return self._state

    # ── Resources ─────────────────────────────────────────────────

    def add_resource(
        self,
        resource_type: str,
        display_name: str,
        *,
        resource_id: str | None = None,
        x: float = 4.0,
        y: float = 4.0,
        width: float = 1.0,
        height: float = 1.0,
        group_id: str | None = None,
        properties: dict | None = None,
    ) -> DiagramResource:
        """Add an Azure resource to the diagram. Auto-generates ID if not provided."""
        rid = resource_id or f"res-{uuid.uuid4().hex[:8]}"
        resource = DiagramResource(
            id=rid,
            resource_type=resource_type,
            display_name=display_name,
            position=Position(x=x, y=y),
            size=Size(width=width, height=height),
            group_id=group_id,
            properties=properties or {},
        )
        self._state.resources[rid] = resource
        return resource

    def remove_resource(self, resource_id: str) -> bool:
        """Remove a resource and all its connections. Returns False if not found."""
        if resource_id not in self._state.resources:
            return False
        del self._state.resources[resource_id]
        # Also remove connections referencing this resource
        to_remove = [
            cid
            for cid, conn in self._state.connections.items()
            if conn.source_id == resource_id or conn.target_id == resource_id
        ]
        for cid in to_remove:
            del self._state.connections[cid]
        return True

    def move_resource(self, resource_id: str, x: float, y: float) -> bool:
        """Move a resource to a new position. Returns False if not found."""
        if resource_id not in self._state.resources:
            return False
        self._state.resources[resource_id].position = Position(x=x, y=y)
        return True

    # ── Connections ───────────────────────────────────────────────

    def add_connection(
        self,
        source_id: str,
        target_id: str,
        *,
        connection_id: str | None = None,
        label: str = "",
        connection_type: str = "data_flow",
        style: str = "solid",
    ) -> Connection:
        """Add a connection between two existing resources. Raises ValueError if either resource is missing."""
        if source_id not in self._state.resources:
            raise ValueError(f"Source resource '{source_id}' not found")
        if target_id not in self._state.resources:
            raise ValueError(f"Target resource '{target_id}' not found")

        cid = connection_id or f"conn-{uuid.uuid4().hex[:8]}"
        conn = Connection(
            id=cid,
            source_id=source_id,
            target_id=target_id,
            label=label,
            connection_type=connection_type,
            style=style,
        )
        self._state.connections[cid] = conn
        return conn

    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection. Returns False if not found."""
        if connection_id not in self._state.connections:
            return False
        del self._state.connections[connection_id]
        return True

    # ── Boundaries ────────────────────────────────────────────────

    def add_boundary(
        self,
        boundary_type: str,
        display_name: str,
        *,
        boundary_id: str | None = None,
        x: float = 1.0,
        y: float = 1.0,
        width: float = 6.0,
        height: float = 4.0,
        parent_id: str | None = None,
        properties: dict | None = None,
    ) -> BoundaryGroup:
        """Add a boundary/container (VNet, subnet, resource group, etc.). Auto-generates ID if not provided."""
        bid = boundary_id or f"bnd-{uuid.uuid4().hex[:8]}"
        boundary = BoundaryGroup(
            id=bid,
            boundary_type=boundary_type,
            display_name=display_name,
            position=Position(x=x, y=y),
            size=Size(width=width, height=height),
            parent_id=parent_id,
            properties=properties or {},
        )
        self._state.boundaries[bid] = boundary
        return boundary

    def remove_boundary(self, boundary_id: str) -> bool:
        """Remove a boundary, unlink its child resources and sub-boundaries. Returns False if not found."""
        if boundary_id not in self._state.boundaries:
            return False
        # Unlink resources assigned to this boundary
        for res in self._state.resources.values():
            if res.group_id == boundary_id:
                res.group_id = None
        # Unlink child boundaries
        for bnd in self._state.boundaries.values():
            if bnd.parent_id == boundary_id:
                bnd.parent_id = None
        del self._state.boundaries[boundary_id]
        return True

    def assign_to_boundary(self, resource_id: str, boundary_id: str) -> bool:
        """Assign a resource to a boundary group. Returns False if either is missing."""
        if resource_id not in self._state.resources:
            return False
        if boundary_id not in self._state.boundaries:
            return False
        self._state.resources[resource_id].group_id = boundary_id
        return True

    # ── Query helpers ─────────────────────────────────────────────

    def get_resources_in_boundary(self, boundary_id: str) -> list[DiagramResource]:
        """Return all resources assigned to the given boundary."""
        return [r for r in self._state.resources.values() if r.group_id == boundary_id]

    def get_connections_for_resource(self, resource_id: str) -> list[Connection]:
        """Return all connections where the resource is source or target."""
        return [
            c
            for c in self._state.connections.values()
            if c.source_id == resource_id or c.target_id == resource_id
        ]

    def summary(self) -> dict:
        """Return a concise summary of the diagram contents."""
        return {
            "name": self._state.name,
            "resource_count": len(self._state.resources),
            "connection_count": len(self._state.connections),
            "boundary_count": len(self._state.boundaries),
            "resources": {
                r.id: {
                    "id": r.id,
                    "type": r.resource_type,
                    "name": r.display_name,
                    "position": {"x": r.position.x, "y": r.position.y},
                    "size": {"width": r.size.width, "height": r.size.height},
                    "group_id": r.group_id,
                    "category": r.properties.get("category", ""),
                }
                for r in self._state.resources.values()
            },
            "connections": {
                c.id: {
                    "id": c.id,
                    "from": c.source_id,
                    "to": c.target_id,
                    "label": c.label,
                    "connection_type": c.connection_type,
                    "style": c.style,
                }
                for c in self._state.connections.values()
            },
            "boundaries": {
                b.id: {
                    "id": b.id,
                    "type": b.boundary_type,
                    "name": b.display_name,
                    "position": {"x": b.position.x, "y": b.position.y},
                    "size": {"width": b.size.width, "height": b.size.height},
                    "parent_id": b.parent_id,
                }
                for b in self._state.boundaries.values()
            },
        }
