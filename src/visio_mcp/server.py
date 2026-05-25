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

# Import shared MCP instance and state
from visio_mcp._state import mcp  # noqa: F401

# Import all tool modules to register tools/resources/prompts with the mcp instance
import visio_mcp.tools  # noqa: F401

# Re-export tool functions for backward compatibility
from visio_mcp.tools.diagram_tools import *  # noqa: F401, F403
from visio_mcp.tools.validation_tools import *  # noqa: F401, F403
from visio_mcp.tools.save_tools import *  # noqa: F401, F403
from visio_mcp.tools.catalog_tools import *  # noqa: F401, F403
from visio_mcp.tools.reference_tools import *  # noqa: F401, F403
from visio_mcp.tools.import_tools import *  # noqa: F401, F403
from visio_mcp.tools.prompts import *  # noqa: F401, F403
from visio_mcp.tools.pricing_tools import *  # noqa: F401, F403


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
