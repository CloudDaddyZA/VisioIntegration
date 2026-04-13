"""Desktop launcher — runs Streamlit + pywebview as a native Windows app.

Starts the Streamlit server in a background thread, then opens a
pywebview window pointing at it. When the window is closed, the
Streamlit process is terminated and the app exits cleanly.

Usage:
    python -m app.desktop          # from project root
    visio-desktop                  # if installed via pip install .[desktop]
"""

from __future__ import annotations

import multiprocessing
import os
import socket
import sys
import time
from pathlib import Path


def _find_free_port() -> int:
    """Find an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 30.0) -> bool:
    """Block until the Streamlit server is accepting connections."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def _run_streamlit(port: int) -> None:
    """Start Streamlit in this process (called in a child process)."""
    # Ensure project root is on sys.path so imports resolve
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root))

    from streamlit.web.cli import main as st_main

    sys.argv = [
        "streamlit", "run",
        str(Path(__file__).resolve().parent / "streamlit_app.py"),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.address", "127.0.0.1",
        "--browser.gatherUsageStats", "false",
        "--global.developmentMode", "false",
    ]
    st_main()


def main() -> None:
    """Entry point for the desktop app."""
    # Avoid issues with multiprocessing + PyInstaller frozen exe
    multiprocessing.freeze_support()

    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"

    # Start Streamlit in a child process
    server = multiprocessing.Process(target=_run_streamlit, args=(port,), daemon=True)
    server.start()

    # Wait for Streamlit to become ready
    if not _wait_for_server(port):
        print("ERROR: Streamlit server did not start within 30 seconds.", file=sys.stderr)
        server.terminate()
        sys.exit(1)

    # Open native window via pywebview
    import webview  # type: ignore[import-untyped]

    window = webview.create_window(
        title="Azure Visio AI Assistant",
        url=url,
        width=1400,
        height=900,
        min_size=(1024, 700),
        text_select=True,
    )
    # webview.start() blocks until the window is closed
    webview.start(private_mode=False)

    # Cleanup
    server.terminate()
    server.join(timeout=5)


if __name__ == "__main__":
    main()
