"""Auto-layout engine for positioning Azure architecture diagram elements.

Layout conventions follow Microsoft Azure Architecture Center standards:
  - Top-to-bottom or left-to-right traffic flow
  - Numbered workflow steps on data-flow arrows
  - Resources grouped inside VNet/subnet/RG boundaries
  - Private endpoints shown explicitly in dedicated subnets
  - Management/identity resources along the bottom or right edge
  - Consistent spacing aligned with official icon sizing (0.6")
"""

from __future__ import annotations

import math
from collections import defaultdict

from .models import DiagramState, Position, Size
from .reference_architectures import MICROSOFT_STANDARDS


class LayoutEngine:
    """Automatically positions resources, boundaries, and connections.

    Uses Microsoft Architecture Center conventions for spacing and flow.
    """

    # Spacing aligned with Microsoft diagram standards
    RESOURCE_H_GAP = MICROSOFT_STANDARDS.resource_h_spacing
    RESOURCE_V_GAP = MICROSOFT_STANDARDS.resource_v_spacing
    BOUNDARY_PADDING = MICROSOFT_STANDARDS.boundary_padding
    BOUNDARY_HEADER = MICROSOFT_STANDARDS.boundary_header_height
    TIER_GAP = 3.0   # Gap between architectural tiers
    PAGE_MARGIN = MICROSOFT_STANDARDS.page_margin

    def auto_layout(
        self,
        state: DiagramState,
        strategy: str = "tiered",
        layout_hints: dict[str, tuple[float, float]] | None = None,
        boundary_hints: dict[str, tuple[float, float, float, float]] | None = None,
    ) -> DiagramState:
        """Apply an auto-layout strategy to the diagram.

        Strategies:
            hints   - Use explicit position hints (from reference architectures)
            tiered  - Arrange in horizontal tiers (ingress -> compute -> data)
            grid    - Simple grid layout
            grouped - Group by boundary, then lay out within each group
        """
        # If explicit hints are provided, use them first then fill gaps
        if layout_hints or boundary_hints:
            self._layout_from_hints(state, layout_hints or {}, boundary_hints or {})
            return state

        if strategy == "tiered":
            self._layout_tiered(state)
        elif strategy == "grid":
            self._layout_grid(state)
        elif strategy == "grouped":
            self._layout_grouped(state)
        else:
            self._layout_grid(state)
        return state

    # ── Hint-based layout ─────────────────────────────────────────

    def _layout_from_hints(
        self,
        state: DiagramState,
        layout_hints: dict[str, tuple[float, float]],
        boundary_hints: dict[str, tuple[float, float, float, float]],
    ) -> None:
        """Apply explicit position hints from reference architecture templates.

        Resources/boundaries with hints get exact positions.
        Resources without hints fall back to tiered auto-layout.
        Boundaries without hints get auto-fitted to their children.
        """
        # Apply boundary hints first (x, y, width, height)
        for bid, (bx, by, bw, bh) in boundary_hints.items():
            if bid in state.boundaries:
                state.boundaries[bid].position = Position(x=bx, y=by)
                state.boundaries[bid].size = Size(width=bw, height=bh)

        # Apply resource position hints
        placed = set()
        for rid, (rx, ry) in layout_hints.items():
            if rid in state.resources:
                state.resources[rid].position = Position(x=rx, y=ry)
                placed.add(rid)

        # Any resources without hints — auto-layout via tiered strategy
        unplaced = [rid for rid in state.resources if rid not in placed]
        if unplaced:
            # Find a safe starting position (below/right of all placed resources)
            max_y = 2.0
            if placed:
                max_y = max(
                    state.resources[rid].position.y for rid in placed
                ) + self.RESOURCE_V_GAP

            tiers: dict[int, list[str]] = defaultdict(list)
            for rid in unplaced:
                tier = self._TIER_MAP.get(state.resources[rid].resource_type, 3)
                tiers[tier].append(rid)

            start_x = 2.0
            for tier_idx in sorted(tiers.keys()):
                rids = tiers[tier_idx]
                x = start_x + tier_idx * self.TIER_GAP
                for i, rid in enumerate(rids):
                    y = max_y + i * self.RESOURCE_V_GAP
                    state.resources[rid].position = Position(x=x, y=y)

        # Fit any boundaries without hints to enclose their children (bottom-up)
        unhinted = [bid for bid in state.boundaries if bid not in boundary_hints]
        # Sort bottom-up using nesting order
        order = self._boundary_nesting_order(state)
        for bid in order:
            if bid in unhinted:
                self._fit_single_boundary(state, bid)

    # ── Tiered layout ─────────────────────────────────────────────

    # Classification of resources into architectural tiers for left-to-right flow
    _TIER_MAP: dict[str, int] = {
        # Tier 0: External / Ingress
        "user": 0, "internet": 0, "on_premises": 0,
        # Tier 1: Edge / Global routing
        "front_door": 1, "traffic_manager": 1, "cdn_profile": 1, "ddos_protection": 1,
        # Tier 2: Gateway / WAF
        "application_gateway": 2, "firewall": 2, "api_management": 2, "bastion": 2,
        "load_balancer": 2, "nat_gateway": 2,
        # Tier 3: Compute
        "virtual_machine": 3, "vm_scale_set": 3, "app_service": 3, "app_service_plan": 3,
        "function_app": 3, "container_apps": 3, "kubernetes_service": 3,
        "container_instances": 3, "static_web_app": 3, "bot_service": 3,
        # Tier 4: Integration / Messaging
        "service_bus": 4, "event_hub": 4, "event_grid": 4, "logic_app": 4, "signalr": 4,
        # Tier 5: Data / Storage
        "sql_database": 5, "sql_managed_instance": 5, "cosmos_db": 5,
        "mysql_database": 5, "postgresql_database": 5, "redis_cache": 5,
        "storage_account": 5, "blob_storage": 5, "data_lake_storage": 5,
        "managed_disk": 5, "file_share": 5,
        # Tier 6: Analytics / AI
        "synapse_analytics": 6, "data_factory": 6, "databricks": 6,
        "stream_analytics": 6, "openai_service": 6, "cognitive_services": 6,
        "machine_learning": 6, "ai_search": 6,
        # Tier 7: Security / Identity / Management (placed at bottom)
        "key_vault": 7, "entra_id": 7, "managed_identity": 7, "app_registration": 7,
        "defender_for_cloud": 7, "sentinel": 7,
        "monitor": 7, "log_analytics": 7, "application_insights": 7,
        "policy": 7, "devops": 7,
        # Networking constructs handled as boundaries
        "virtual_network": 7, "subnet": 7, "nsg": 7, "private_endpoint": 7,
        "private_link": 7, "vpn_gateway": 7, "expressroute": 7, "dns_zone": 7,
        # Management hierarchy
        "resource_group": 7, "subscription": 7, "management_group": 7,
        # IoT
        "iot_hub": 4, "iot_central": 4,
        "container_registry": 4,
    }

    def _layout_tiered(self, state: DiagramState) -> None:
        """Arrange resources in horizontal tiers from left to right."""
        tiers: dict[int, list[str]] = defaultdict(list)

        for rid, res in state.resources.items():
            tier = self._TIER_MAP.get(res.resource_type, 3)
            tiers[tier].append(rid)

        start_x = 2.0
        start_y = 2.0

        for tier_idx in sorted(tiers.keys()):
            rids = tiers[tier_idx]
            x = start_x + tier_idx * self.TIER_GAP
            for i, rid in enumerate(rids):
                y = start_y + i * self.RESOURCE_V_GAP
                state.resources[rid].position = Position(x=x, y=y)

        # Resize boundaries to enclose their resources
        self._fit_boundaries(state)

    # ── Grid layout ───────────────────────────────────────────────

    def _layout_grid(self, state: DiagramState) -> None:
        """Simple grid layout."""
        resources = list(state.resources.values())
        cols = max(1, math.ceil(math.sqrt(len(resources))))
        start_x = 2.0
        start_y = 2.0

        for idx, res in enumerate(resources):
            col = idx % cols
            row = idx // cols
            res.position = Position(
                x=start_x + col * self.RESOURCE_H_GAP,
                y=start_y + row * self.RESOURCE_V_GAP,
            )

        self._fit_boundaries(state)

    # ── Grouped layout ────────────────────────────────────────────

    def _layout_grouped(self, state: DiagramState) -> None:
        """Group resources by their boundary, then lay out each group."""
        grouped: dict[str | None, list[str]] = defaultdict(list)
        for rid, res in state.resources.items():
            grouped[res.group_id].append(rid)

        current_x = 2.0

        # Layout each boundary group
        for group_id in [None] + list(state.boundaries.keys()):
            rids = grouped.get(group_id, [])
            if not rids:
                continue

            cols = max(1, math.ceil(math.sqrt(len(rids))))
            group_start_x = current_x
            group_start_y = 3.0

            for idx, rid in enumerate(rids):
                col = idx % cols
                row = idx // cols
                state.resources[rid].position = Position(
                    x=group_start_x + self.BOUNDARY_PADDING + col * self.RESOURCE_H_GAP,
                    y=group_start_y + self.BOUNDARY_HEADER + row * self.RESOURCE_V_GAP,
                )

            # Resize boundary to fit
            if group_id and group_id in state.boundaries:
                max_col = min(len(rids), cols)
                num_rows = math.ceil(len(rids) / cols)
                bnd = state.boundaries[group_id]
                bnd.position = Position(x=group_start_x, y=group_start_y - self.BOUNDARY_HEADER)
                bnd.size = Size(
                    width=max_col * self.RESOURCE_H_GAP + 2 * self.BOUNDARY_PADDING,
                    height=num_rows * self.RESOURCE_V_GAP + self.BOUNDARY_HEADER + self.BOUNDARY_PADDING,
                )

            current_x += (min(len(rids), cols if rids else 1)) * self.RESOURCE_H_GAP + 2 * self.BOUNDARY_PADDING + 1.0

    # ── Helpers ───────────────────────────────────────────────────

    def _fit_boundaries(self, state: DiagramState) -> None:
        """Resize boundaries to enclose their assigned resources and child boundaries.

        Processes bottom-up: innermost boundaries (subnets) first, then
        their parents (vnets), then grandparents (resource_groups, subscriptions).
        This ensures parent boundaries account for already-fitted child boundaries.
        After fitting, sibling boundaries at the same nesting level are aligned.
        """
        # Build nesting order — leaves first, then parents
        order = self._boundary_nesting_order(state)
        for bid in order:
            self._fit_single_boundary(state, bid)

        # Align sibling boundaries that share the same parent
        self._align_sibling_boundaries(state)

        # Re-fit parents after alignment since children may have shifted
        for bid in reversed(order):
            bnd = state.boundaries.get(bid)
            if bnd and bnd.parent_id:
                # Only re-fit ancestors
                continue
        # Do a second pass for parents to pick up aligned children
        parent_ids = {
            bnd.parent_id for bnd in state.boundaries.values() if bnd.parent_id
        }
        for bid in order:
            if bid in parent_ids:
                self._fit_single_boundary(state, bid)

    def _boundary_nesting_order(self, state: DiagramState) -> list[str]:
        """Return boundary IDs sorted bottom-up: leaves first, root last."""
        children_of: dict[str | None, list[str]] = {}
        for bid, bnd in state.boundaries.items():
            children_of.setdefault(bnd.parent_id, []).append(bid)

        order: list[str] = []
        visited: set[str] = set()

        def visit(bid: str) -> None:
            if bid in visited:
                return
            # Visit children first (depth-first, post-order)
            for child in children_of.get(bid, []):
                visit(child)
            visited.add(bid)
            order.append(bid)

        for bid in state.boundaries:
            visit(bid)
        return order

    def _align_sibling_boundaries(self, state: DiagramState) -> None:
        """Align boundaries that share the same parent to consistent tops and heights."""
        # Group boundaries by parent
        siblings: dict[str | None, list[str]] = {}
        for bid, bnd in state.boundaries.items():
            siblings.setdefault(bnd.parent_id, []).append(bid)

        for parent_id, sib_ids in siblings.items():
            if len(sib_ids) < 2:
                continue

            # Align top edges — use the topmost y among siblings
            min_y = min(state.boundaries[bid].position.y for bid in sib_ids)
            # Align heights — use the tallest
            max_h = max(state.boundaries[bid].size.height for bid in sib_ids)

            for bid in sib_ids:
                bnd = state.boundaries[bid]
                bnd.position = Position(x=bnd.position.x, y=min_y)
                bnd.size = Size(width=bnd.size.width, height=max_h)

    def _fit_single_boundary(self, state: DiagramState, bid: str) -> None:
        """Resize a single boundary to enclose its assigned resources AND child boundaries."""
        boundary = state.boundaries.get(bid)
        if not boundary:
            return

        # Collect extents from direct child resources
        children = [
            r for r in state.resources.values() if r.group_id == bid
        ]

        # Collect extents from child boundaries (nested boundaries with parent_id == bid)
        child_boundaries = [
            b for b in state.boundaries.values() if b.parent_id == bid
        ]

        if not children and not child_boundaries:
            return

        extents: list[tuple[float, float, float, float]] = []  # (left, right, top, bottom)

        for r in children:
            extents.append((
                r.position.x - r.size.width / 2,
                r.position.x + r.size.width / 2,
                r.position.y - r.size.height / 2,
                r.position.y + r.size.height / 2,
            ))

        for cb in child_boundaries:
            extents.append((
                cb.position.x,
                cb.position.x + cb.size.width,
                cb.position.y,
                cb.position.y + cb.size.height,
            ))

        if not extents:
            return

        min_x = min(e[0] for e in extents)
        max_x = max(e[1] for e in extents)
        min_y = min(e[2] for e in extents)
        max_y = max(e[3] for e in extents)

        boundary.position = Position(
            x=min_x - self.BOUNDARY_PADDING,
            y=min_y - self.BOUNDARY_PADDING - self.BOUNDARY_HEADER,
        )
        boundary.size = Size(
            width=(max_x - min_x) + 2 * self.BOUNDARY_PADDING,
            height=(max_y - min_y) + 2 * self.BOUNDARY_PADDING + self.BOUNDARY_HEADER,
        )
