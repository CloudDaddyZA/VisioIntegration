"""Clipboard paste image component for Streamlit.

Uses a bidirectional Streamlit component to capture pasted images
from the clipboard (screenshots, snipping tool, etc.) and return
them as base64 data URLs.
"""
from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).parent / "paste_image_frontend"

_paste_image = components.declare_component("paste_image", path=str(_COMPONENT_DIR))


def paste_image_component(key: str = "paste_image", height: int = 120) -> str | None:
    """Render a paste-target that captures clipboard images.

    Returns:
        Base64 data URL string (e.g. "data:image/png;base64,...") if an image
        was pasted, or None.
    """
    value = _paste_image(key=key, default=None, height=height)
    return value
