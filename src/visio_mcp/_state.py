"""Shared MCP server instance and singleton state for tool modules.

All tool submodules import from here to avoid circular dependencies.
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from .caf_validator import CafValidator
from .diagram_state import DiagramManager
from .layout_engine import LayoutEngine
from .waf_validator import WafValidator

logger = logging.getLogger(__name__)

# ── MCP server instance ───────────────────────────────────────────

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

# ── Singleton instances ───────────────────────────────────────────

_diagram = DiagramManager()
_layout = LayoutEngine()
_waf = WafValidator()
_caf = CafValidator()
