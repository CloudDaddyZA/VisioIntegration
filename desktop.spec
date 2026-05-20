# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Azure Visio AI Assistant.

Build with:
    pyinstaller desktop.spec --noconfirm

Or use the helper script:
    python scripts/build_desktop.py
"""

import os
import sys
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────
ROOT = Path(SPECPATH).resolve()
SRC = ROOT / "src"
APP = ROOT / "app"
STENCILS = SRC / "visio_mcp" / "stencils"

# ── Collect Streamlit's runtime data ──────────────────────────────
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

streamlit_datas = collect_data_files("streamlit")
streamlit_hiddens = collect_submodules("streamlit")

# ── Analysis ──────────────────────────────────────────────────────
a = Analysis(
    [str(APP / "desktop.py")],
    pathex=[str(SRC), str(ROOT)],
    binaries=[],
    datas=[
        # App source files (Streamlit needs to read them at runtime)
        (str(APP / "streamlit_app.py"), "app"),
        (str(APP / "ai_agent.py"), "app"),
        (str(APP / "mcp_client.py"), "app"),
        (str(APP / "diagram_preview.py"), "app"),
        (str(APP / "run.py"), "app"),
        (str(APP / "__init__.py"), "app"),
        # App components (paste image, etc.)
        (str(APP / "components"), "app/components"),
        # App assets (logo, etc.)
        (str(APP / "assets"), "app/assets"),
        # MCP server package
        (str(SRC / "visio_mcp"), "visio_mcp"),
        # Stencil SVG icons (if present)
        *( [(str(STENCILS), "visio_mcp/stencils")] if STENCILS.exists() else [] ),
        # Streamlit runtime files
        *streamlit_datas,
    ],
    hiddenimports=[
        # App modules
        "app.streamlit_app",
        "app.ai_agent",
        "app.mcp_client",
        "app.diagram_preview",
        # MCP server modules
        "visio_mcp",
        "visio_mcp.server",
        "visio_mcp.azure_catalog",
        "visio_mcp.caf_validator",
        "visio_mcp.diagram_state",
        "visio_mcp.drawio_engine",
        "visio_mcp.layout_engine",
        "visio_mcp.models",
        "visio_mcp.reference_architectures",
        "visio_mcp.visio_engine",
        "visio_mcp.waf_validator",
        "visio_mcp.azure_sku_grounding",
        "visio_mcp.pricing_import",
        # pywebview backend
        "webview",
        # pywin32 (Visio COM)
        "win32com",
        "win32com.client",
        "pythoncom",
        "pywintypes",
        # Streamlit hidden imports
        *streamlit_hiddens,
        # Common transitive deps
        "pydantic",
        "openai",
        "mcp",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AzureVisioAssistant",
    icon=None,  # Use .ico version of logo if available
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # windowed app — no terminal
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AzureVisioAssistant",
)
