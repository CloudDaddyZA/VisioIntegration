"""Mermaid rendering engine for Azure architecture diagrams.

Converts a DiagramState into Mermaid ``flowchart`` syntax that can be embedded
in Markdown, GitHub/GitLab READMes, docs sites, or rendered at mermaid.live.

Boundaries (resource groups, VNets, subnets, etc.) become nested ``subgraph``
blocks. Resources become labeled nodes coloured by their Azure service category.
Connections become edges, with solid/dashed styles mapped from the connection
type.

The output is plain text (``.mmd`` by convention). It is intentionally
dependency-free and works without Visio, draw.io, or any icon packs installed.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from .azure_catalog import BOUNDARY_STYLES, get_shape, resolve_alias
from .models import BoundaryGroup, Connection, DiagramResource, DiagramState

logger = logging.getLogger(__name__)


# ── Connection style → Mermaid link syntax ───────────────────────
# Mermaid flowcharts support solid (-->) and dotted (-.->) links.
# Dashed connection types are mapped to the dotted link form.
_LINK_BY_STYLE = {
    "solid": "-->",
    "dashed": "-.->",
    "dotted": "-.->",
}
_LINK_BY_STYLE_LABELLED = {
    "solid": "-->|{label}|",
    "dashed": "-.->|{label}|",
    "dotted": "-.->|{label}|",
}


def _sanitize_id(raw: str, used: set[str]) -> str:
    """Produce a Mermaid-safe node/subgraph id, unique within ``used``."""
    safe = re.sub(r"[^0-9A-Za-z_]", "_", raw).strip("_")
    if not safe or safe[0].isdigit():
        safe = f"n_{safe}" if safe else "n"
    candidate = safe
    i = 1
    while candidate in used:
        candidate = f"{safe}_{i}"
        i += 1
    used.add(candidate)
    return candidate


def _escape_label(text: str) -> str:
    """Escape a label for use inside a Mermaid ["..."] node."""
    if not text:
        return ""
    return (
        text.replace("\\", "")
        .replace('"', "&quot;")
        .replace("\n", "<br/>")
        .strip()
    )


def _humanize(resource_type: str) -> str:
    """Turn a resource_type key into a human-readable type label."""
    shape = get_shape(resource_type)
    if shape is not None:
        return shape.display_name
    return resource_type.replace("_", " ").title()


class MermaidEngine:
    """Render a DiagramState to Mermaid flowchart text."""

    def __init__(self, direction: str = "TB") -> None:
        # TB (top-bottom), LR (left-right), etc.
        self.direction = direction if direction in ("TB", "TD", "LR", "RL", "BT") else "TB"
        self._ids: dict[str, str] = {}  # original id → mermaid id
        self._used: set[str] = set()
        self._classes: dict[str, str] = {}  # class name → classDef style

    # ── Public API ────────────────────────────────────────────────
    def render(self, state: DiagramState, output_path: str) -> str:
        """Render the diagram state to a .mmd file. Returns the output path."""
        output_path = os.path.abspath(output_path)
        text = self.render_text(state)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(text, encoding="utf-8")
        logger.info("Diagram saved to %s (mermaid)", output_path)
        return output_path

    def render_text(self, state: DiagramState) -> str:
        """Render the diagram state to a Mermaid flowchart string."""
        self._ids = {}
        self._used = set()
        self._classes = {}

        # Assign mermaid ids up-front for all boundaries and resources.
        for bid in state.boundaries:
            self._ids[bid] = _sanitize_id(bid, self._used)
        for rid in state.resources:
            self._ids[rid] = _sanitize_id(rid, self._used)

        lines: list[str] = []
        title = _escape_label(state.name) or "Azure Architecture"
        lines.append("---")
        lines.append(f"title: {title}")
        lines.append("---")
        lines.append(f"flowchart {self.direction}")

        # Build boundary nesting tree.
        children_of: dict[str | None, list[BoundaryGroup]] = {}
        for b in state.boundaries.values():
            children_of.setdefault(b.parent_id, []).append(b)

        # Resources grouped by their boundary.
        resources_in: dict[str | None, list[DiagramResource]] = {}
        for r in state.resources.values():
            key = r.group_id if r.group_id in state.boundaries else None
            resources_in.setdefault(key, []).append(r)

        body: list[str] = []

        # Top-level boundaries (no parent or missing parent).
        valid_ids = set(state.boundaries)
        top_boundaries = [
            b for b in state.boundaries.values()
            if b.parent_id is None or b.parent_id not in valid_ids
        ]
        for boundary in top_boundaries:
            self._render_boundary(boundary, children_of, resources_in, body, indent=1)

        # Ungrouped resources at the top level.
        for resource in resources_in.get(None, []):
            body.append("    " + self._resource_node(resource))

        # Connections.
        for conn in state.connections.values():
            edge = self._connection_edge(conn)
            if edge:
                body.append("    " + edge)

        lines.extend(body)

        # classDef definitions + class assignments.
        if self._classes:
            lines.append("")
            for cname, style in sorted(self._classes.items()):
                lines.append(f"    classDef {cname} {style}")

        return "\n".join(lines) + "\n"

    # ── Internal helpers ──────────────────────────────────────────
    def _render_boundary(
        self,
        boundary: BoundaryGroup,
        children_of: dict[str | None, list[BoundaryGroup]],
        resources_in: dict[str | None, list[DiagramResource]],
        out: list[str],
        indent: int,
    ) -> None:
        pad = "    " * indent
        mid = self._ids[boundary.id]
        label = _escape_label(boundary.display_name) or boundary.boundary_type
        btype = _escape_label(boundary.boundary_type.replace("_", " ").title())
        full_label = f"{label}<br/><i>{btype}</i>" if btype else label
        out.append(f'{pad}subgraph {mid}["{full_label}"]')
        out.append(f"{pad}    direction {self.direction}")

        # Nested child boundaries.
        for child in children_of.get(boundary.id, []):
            self._render_boundary(child, children_of, resources_in, out, indent + 1)

        # Resources directly inside this boundary.
        for resource in resources_in.get(boundary.id, []):
            out.append(f"{pad}    " + self._resource_node(resource))

        out.append(f"{pad}end")

        # Style the subgraph from the boundary palette.
        cname = self._boundary_class(boundary.boundary_type)
        if cname:
            out.append(f"{pad}class {mid} {cname}")

    def _resource_node(self, resource: DiagramResource) -> str:
        mid = self._ids[resource.id]
        name = _escape_label(resource.display_name) or resource.id
        rtype = _humanize(resource.resource_type)
        label = f"{name}<br/><i>{_escape_label(rtype)}</i>"
        node = f'{mid}["{label}"]'
        cname = self._resource_class(resource.resource_type)
        if cname:
            node += f"\n    class {mid} {cname}"
        return node

    def _connection_edge(self, conn: Connection) -> str | None:
        src = self._ids.get(conn.source_id)
        tgt = self._ids.get(conn.target_id)
        if not src or not tgt:
            return None
        style = (conn.style or "solid").lower()
        label = _escape_label(conn.label)
        if label:
            link = _LINK_BY_STYLE_LABELLED.get(style, "-->|{label}|").format(label=label)
        else:
            link = _LINK_BY_STYLE.get(style, "-->")
        return f"{src} {link} {tgt}"

    def _boundary_class(self, boundary_type: str) -> str:
        bstyle = BOUNDARY_STYLES.get(boundary_type) or BOUNDARY_STYLES.get(
            resolve_alias(boundary_type)
        )
        if not bstyle:
            return ""
        cname = "b_" + re.sub(r"[^0-9A-Za-z_]", "_", boundary_type)
        if cname not in self._classes:
            fill = bstyle.get("fill_color", "#F0F0F0")
            stroke = bstyle.get("line_color", "#808080")
            dash = ""
            if bstyle.get("line_pattern") in ("dashed", "dotted"):
                dash = ",stroke-dasharray: 5 5"
            self._classes[cname] = f"fill:{fill},stroke:{stroke},color:#333{dash}"
        return cname

    def _resource_class(self, resource_type: str) -> str:
        shape = get_shape(resource_type)
        if shape is None:
            return ""
        category = shape.category.value
        cname = "c_" + re.sub(r"[^0-9A-Za-z_]", "_", category)
        if cname not in self._classes:
            fill = shape.icon_color or "#0078D4"
            self._classes[cname] = f"fill:{fill},stroke:#333,color:#fff"
        return cname
