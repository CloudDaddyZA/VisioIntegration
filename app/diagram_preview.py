"""SVG preview renderer for the diagram state in the browser."""

from __future__ import annotations

import html
from typing import Any

# Color palette matching Azure Architecture Center standards
BOUNDARY_COLORS = {
    "subscription": ("#E5E5E5", "#999999"),
    "resource_group": ("#F2F2F2", "#BBBBBB"),
    "vnet": ("#DEEAF6", "#5B9BD5"),
    "subnet": ("#E2F0D9", "#70AD47"),
    "availability_zone": ("#FFF2CC", "#ED7D31"),
    "region": ("#F2F2F2", "#666666"),
    "management_group": ("#E8E0EE", "#7030A0"),
    "nsg": ("#FCE4EC", "#E74856"),
}

CONNECTOR_COLORS = {
    "data_flow": "#0078D4",
    "network": "#107C10",
    "dependency": "#666666",
    "reference": "#999999",
    "vpn_tunnel": "#7030A0",
    "expressroute": "#FF8C00",
    "private_link": "#E74856",
    "identity": "#FFB900",
}

CATEGORY_COLORS = {
    "Compute": "#0078D4",
    "Networking": "#107C10",
    "Storage": "#0063B1",
    "Databases": "#E74856",
    "Security": "#D83B01",
    "Identity": "#FFB900",
    "Integration": "#8764B8",
    "Analytics": "#00B7C3",
    "AI + Machine Learning": "#881798",
    "DevOps": "#0078D4",
    "Management + Governance": "#515C6B",
    "Web": "#0078D4",
    "Containers": "#326CE5",
    "IoT": "#107C10",
    "General": "#515C6B",
}


def render_diagram_svg(state: dict[str, Any], width: int = 1100, height: int = 750, page_filter: int | None = None) -> str:
    """Render a diagram state dict as an SVG string for browser display.

    Args:
        state: The diagram state dict (from get_diagram_state).
        width: SVG canvas width in pixels.
        height: SVG canvas height in pixels.
        page_filter: If set, only render resources/boundaries/connections from this page number.

    Returns:
        SVG markup string.
    """
    all_resources = state.get("resources", {})
    all_connections = state.get("connections", {})
    all_boundaries = state.get("boundaries", {})
    name = state.get("name", "Diagram")
    page_w = state.get("page_width", 22.0)
    page_h = state.get("page_height", 17.0)

    # Filter by page if requested
    if page_filter is not None:
        resources = {
            rid: r for rid, r in (all_resources.items() if isinstance(all_resources, dict) else [])
            if _get_field(r, "page", default=None) == page_filter
        }
        boundaries = {
            bid: b for bid, b in (all_boundaries.items() if isinstance(all_boundaries, dict) else [])
            if _get_field(b, "page", default=None) == page_filter
        }
        # Include connections where both endpoints are on this page
        page_rids = set(resources.keys())
        connections = {
            cid: c for cid, c in (all_connections.items() if isinstance(all_connections, dict) else [])
            if _get_field(c, "source_id", "from", default="") in page_rids
            and _get_field(c, "target_id", "to", default="") in page_rids
        }
    else:
        resources = all_resources
        connections = all_connections
        boundaries = all_boundaries

    # When filtering by page, compute bounding box of visible elements
    # to normalize positions (undo the multi-page Y stacking offset)
    origin_x = 0.0
    origin_y = 0.0
    if page_filter is not None:
        ys: list[float] = []
        xs: list[float] = []
        for r in (resources.values() if isinstance(resources, dict) else []):
            pos = _get_field(r, "position", default={})
            xs.append(_to_float(pos, "x", 0.0))
            ys.append(_to_float(pos, "y", 0.0))
        for b in (boundaries.values() if isinstance(boundaries, dict) else []):
            pos = _get_field(b, "position", default={})
            xs.append(_to_float(pos, "x", 0.0))
            ys.append(_to_float(pos, "y", 0.0))
        if ys:
            origin_y = min(ys)
        if xs:
            origin_x = min(xs)
        # Add small margin so shapes aren't flush with the edge
        origin_x = max(0.0, origin_x - 1.0)
        origin_y = max(0.0, origin_y - 1.0)

    # Scale: convert inches to pixels
    scale_x = (width - 40) / page_w
    scale_y = (height - 80) / page_h
    scale = min(scale_x, scale_y)

    def tx(x: float) -> float:
        return 20 + (x - origin_x) * scale

    def ty(y: float) -> float:
        return 60 + (y - origin_y) * scale

    parts: list[str] = []

    # SVG header
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'style="background: #FAFAFA; border-radius: 8px; font-family: Segoe UI, sans-serif;">'
    )

    # Defs for arrowheads and filters
    parts.append("""
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#0078D4"/>
        </marker>
        <marker id="arrow-green" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#107C10"/>
        </marker>
        <marker id="arrow-gray" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#666666"/>
        </marker>
        <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
            <feDropShadow dx="1" dy="1" stdDeviation="2" flood-opacity="0.15"/>
        </filter>
    </defs>
    """)

    # Title
    parts.append(
        f'<text x="{width // 2}" y="30" text-anchor="middle" '
        f'font-size="18" font-weight="600" fill="#1A1A1A">'
        f'{html.escape(name)}</text>'
    )

    # Draw boundaries (sorted by area, largest first so they render behind)
    sorted_boundaries = sorted(
        boundaries.values() if isinstance(boundaries, dict) else boundaries,
        key=lambda b: _get_area(b),
        reverse=True,
    )

    for b in sorted_boundaries:
        btype = _get_field(b, "boundary_type", "type", default="resource_group")
        bname = _get_field(b, "display_name", "name", default="")
        pos = _get_field(b, "position", default={})
        size = _get_field(b, "size", default={})

        bx = tx(_to_float(pos, "x", 1.0))
        by = ty(_to_float(pos, "y", 1.0))
        bw = _to_float(size, "width", 6.0) * scale
        bh = _to_float(size, "height", 4.0) * scale

        fill, stroke = BOUNDARY_COLORS.get(btype, ("#F2F2F2", "#BBBBBB"))
        dash = ' stroke-dasharray="8,4"' if btype in ("vnet", "subnet") else ""

        parts.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            f'rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash} opacity="0.7"/>'
        )
        parts.append(
            f'<text x="{bx + 8:.1f}" y="{by + 16:.1f}" font-size="11" '
            f'font-weight="600" fill="{stroke}">{html.escape(bname)}</text>'
        )

    # Draw connections
    res_positions = {}
    for rid, r in (resources.items() if isinstance(resources, dict) else []):
        pos = _get_field(r, "position", default={})
        res_positions[rid] = (
            tx(_to_float(pos, "x", 4.0)),
            ty(_to_float(pos, "y", 4.0)),
        )

    for conn in (connections.values() if isinstance(connections, dict) else connections):
        src_id = _get_field(conn, "source_id", "from", default="")
        tgt_id = _get_field(conn, "target_id", "to", default="")
        label = _get_field(conn, "label", default="")
        ctype = _get_field(conn, "connection_type", "type", default="data_flow")
        style = _get_field(conn, "style", default="solid")

        if src_id not in res_positions or tgt_id not in res_positions:
            continue

        sx, sy = res_positions[src_id]
        ex, ey = res_positions[tgt_id]

        color = CONNECTOR_COLORS.get(ctype, "#0078D4")
        marker = "arrow"
        if color == "#107C10":
            marker = "arrow-green"
        elif color == "#666666":
            marker = "arrow-gray"

        dash = ""
        if style == "dashed":
            dash = ' stroke-dasharray="8,4"'
        elif style == "dotted":
            dash = ' stroke-dasharray="3,3"'

        # Offset line ends to not overlap resource boxes
        parts.append(
            f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
            f'stroke="{color}" stroke-width="1.5"{dash} marker-end="url(#{marker})"/>'
        )

        if label:
            mx = (sx + ex) / 2
            my = (sy + ey) / 2 - 6
            parts.append(
                f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" '
                f'font-size="9" fill="{color}" font-weight="500">'
                f'{html.escape(label)}</text>'
            )

    # Draw resources
    for rid, r in (resources.items() if isinstance(resources, dict) else []):
        pos = _get_field(r, "position", default={})
        rtype = _get_field(r, "resource_type", "type", default="")
        rname = _get_field(r, "display_name", "name", default=rid)
        cat = _get_field(r, "category", default="General")

        rx = tx(_to_float(pos, "x", 4.0))
        ry = ty(_to_float(pos, "y", 4.0))

        # Resource box
        box_w, box_h = 44, 44
        color = _resource_color(rtype, cat)

        parts.append(
            f'<rect x="{rx - box_w / 2:.1f}" y="{ry - box_h / 2:.1f}" '
            f'width="{box_w}" height="{box_h}" rx="6" '
            f'fill="white" stroke="{color}" stroke-width="1.5" filter="url(#shadow)"/>'
        )

        # Icon placeholder (colored circle with initials)
        initials = _initials(rtype)
        parts.append(
            f'<circle cx="{rx:.1f}" cy="{ry - 4:.1f}" r="12" fill="{color}" opacity="0.15"/>'
        )
        parts.append(
            f'<text x="{rx:.1f}" y="{ry:.1f}" text-anchor="middle" '
            f'font-size="10" font-weight="700" fill="{color}">{initials}</text>'
        )

        # Label below
        parts.append(
            f'<text x="{rx:.1f}" y="{ry + box_h / 2 + 12:.1f}" text-anchor="middle" '
            f'font-size="9" fill="#333">{html.escape(_truncate(rname, 18))}</text>'
        )

    # Resource count badge
    n_res = len(resources) if isinstance(resources, dict) else 0
    n_conn = len(connections) if isinstance(connections, dict) else 0
    n_bound = len(boundaries) if isinstance(boundaries, dict) else 0
    parts.append(
        f'<text x="20" y="{height - 10}" font-size="10" fill="#888">'
        f'{n_res} resources \u00b7 {n_conn} connections \u00b7 {n_bound} boundaries</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def render_diagram_html(state: dict[str, Any], width: int = 1100, height: int = 750) -> str:
    """Render diagram state as HTML, with page tabs if the diagram has multiple pages.

    Falls back to a plain SVG when the diagram has no page metadata.
    """
    pages = state.get("pages", [])

    # No pages metadata – single SVG, wrap in minimal HTML
    if not pages:
        svg = render_diagram_svg(state, width=width, height=height)
        return svg

    # Build tabbed HTML
    tab_css = """
    <style>
      .page-tabs { display:flex; gap:4px; margin-bottom:6px; }
      .page-tab {
        padding:6px 16px; border:1px solid #ccc; border-bottom:none;
        border-radius:6px 6px 0 0; background:#f0f0f0; cursor:pointer;
        font-family:Segoe UI,sans-serif; font-size:13px; font-weight:500;
        color:#333;
      }
      .page-tab.active { background:#fff; border-bottom:1px solid #fff; color:#0078D4; font-weight:600; }
      .page-panel { display:none; }
      .page-panel.active { display:block; }
    </style>
    """

    tab_buttons: list[str] = []
    panels: list[str] = []

    for idx, pg in enumerate(pages):
        pg_num = pg.get("number", idx)
        pg_name = html.escape(pg.get("name", f"Page {pg_num + 1}"))
        active = " active" if idx == 0 else ""

        tab_buttons.append(
            f'<div class="page-tab{active}" onclick="switchTab({idx})" id="tab-{idx}">{pg_name}</div>'
        )

        svg = render_diagram_svg(state, width=width, height=height, page_filter=pg_num)
        panels.append(f'<div class="page-panel{active}" id="panel-{idx}">{svg}</div>')

    tab_js = """
    <script>
    function switchTab(idx) {
      document.querySelectorAll('.page-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.page-panel').forEach(p => p.classList.remove('active'));
      document.getElementById('tab-' + idx).classList.add('active');
      document.getElementById('panel-' + idx).classList.add('active');
    }
    </script>
    """

    return (
        tab_css
        + '<div class="page-tabs">' + "".join(tab_buttons) + "</div>"
        + "".join(panels)
        + tab_js
    )


# ── Helpers ───────────────────────────────────────────────────────

def _get_field(obj: Any, *keys: str, default: Any = "") -> Any:
    """Get a field from a dict or pydantic model by trying multiple key names."""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj:
                return obj[k]
        return default
    for k in keys:
        if hasattr(obj, k):
            return getattr(obj, k)
    return default


def _to_float(obj: Any, key: str, default: float = 0.0) -> float:
    """Extract a numeric value from a dict or model attribute, with fallback default."""
    if isinstance(obj, dict):
        return float(obj.get(key, default))
    return float(getattr(obj, key, default))


def _get_area(b: Any) -> float:
    """Calculate boundary area (width * height) for z-order sorting (largest first)."""
    size = _get_field(b, "size", default={})
    return _to_float(size, "width", 6.0) * _to_float(size, "height", 4.0)


def _resource_color(rtype: str, category: str = "General") -> str:
    """Pick a hex color for a resource based on its type keywords, falling back to category."""
    rtype_lower = rtype.lower()
    if any(k in rtype_lower for k in ("vm", "compute", "app_service", "function")):
        return CATEGORY_COLORS["Compute"]
    if any(k in rtype_lower for k in ("vnet", "subnet", "gateway", "firewall", "dns", "load_balancer", "bastion", "front_door", "endpoint", "nsg", "nat", "cdn")):
        return CATEGORY_COLORS["Networking"]
    if any(k in rtype_lower for k in ("storage", "blob", "disk", "file_share", "data_lake")):
        return CATEGORY_COLORS["Storage"]
    if any(k in rtype_lower for k in ("sql", "cosmos", "mysql", "postgres", "redis", "database")):
        return CATEGORY_COLORS["Databases"]
    if any(k in rtype_lower for k in ("key_vault", "defender", "sentinel", "nsg")):
        return CATEGORY_COLORS["Security"]
    if any(k in rtype_lower for k in ("entra", "identity", "managed_identity", "app_registration")):
        return CATEGORY_COLORS["Identity"]
    if any(k in rtype_lower for k in ("openai", "cognitive", "ml", "ai_search", "bot")):
        return CATEGORY_COLORS["AI + Machine Learning"]
    if any(k in rtype_lower for k in ("container", "kubernetes", "aks", "registry")):
        return CATEGORY_COLORS["Containers"]
    if any(k in rtype_lower for k in ("monitor", "log_analytics", "insights")):
        return CATEGORY_COLORS["Management + Governance"]
    return CATEGORY_COLORS.get(category, "#515C6B")


def _initials(rtype: str) -> str:
    """Generate 2-char initials from a resource type key (e.g. 'app_service' -> 'AS')."""
    parts = rtype.replace("_", " ").split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return rtype[:2].upper()


def _truncate(text: str, max_len: int) -> str:
    return text if len(text) <= max_len else text[: max_len - 1] + "\u2026"
