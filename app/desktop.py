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
import tempfile
import threading
import time
from pathlib import Path


def _ensure_std_streams() -> None:
    """Guarantee sys.stdout/sys.stderr are writable.

    In a PyInstaller windowed build (``console=False``) both streams are
    ``None``. Streamlit, logging, and ``importlib.metadata`` all write to
    them, so a ``None`` stream surfaces as
    ``'NoneType' object has no attribute 'write'`` and crashes the app.
    Route any missing stream to a log file (falling back to os.devnull) so
    the app stays alive and errors remain diagnosable.

    Runs at import time so it also covers multiprocessing spawn children,
    which re-import this module.
    """
    if sys.stdout is not None and sys.stderr is not None:
        return
    try:
        log_path = Path(tempfile.gettempdir()) / "AzureVisioAssistant.log"
        sink = open(log_path, "a", buffering=1, encoding="utf-8")
    except Exception:
        sink = open(os.devnull, "w")
    if sys.stdout is None:
        sys.stdout = sink
    if sys.stderr is None:
        sys.stderr = sink


_ensure_std_streams()


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


def _app_dir() -> Path:
    """Directory containing streamlit_app.py.

    In a PyInstaller build the app sources are bundled under
    ``<_MEIPASS>/app``; in a normal checkout they sit next to this file.
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "app"
    return Path(__file__).resolve().parent


def _run_streamlit(port: int) -> None:
    """Start Streamlit in this process (called in a background thread)."""
    # Windowed frozen children inherit None std streams — re-guard here.
    _ensure_std_streams()

    # Streamlit's bootstrap installs SIGTERM/SIGINT handlers, but
    # signal.signal() only works on the main thread. We run Streamlit on a
    # daemon thread (pywebview owns the main thread), so make signal.signal
    # a no-op off the main thread instead of letting it raise ValueError.
    import signal as _signal

    _orig_signal = _signal.signal

    def _safe_signal(sig, handler):  # noqa: ANN001
        try:
            return _orig_signal(sig, handler)
        except ValueError:
            return None  # not on main thread — ignore

    _signal.signal = _safe_signal

    app_dir = _app_dir()

    # Ensure import roots are on sys.path so app/visio_mcp imports resolve.
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS"))
        for p in (meipass, app_dir):
            sys.path.insert(0, str(p))
    else:
        root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(root / "src"))
        sys.path.insert(0, str(root))

    from streamlit.web.cli import main as st_main

    sys.argv = [
        "streamlit", "run",
        str(app_dir / "streamlit_app.py"),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.address", "127.0.0.1",
        "--browser.gatherUsageStats", "false",
        "--global.developmentMode", "false",
    ]
    st_main()


def main() -> None:
    """Entry point for the desktop app."""
    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"

    # Start Streamlit in a background *thread* (not a child process).
    #
    # In a PyInstaller windowed build, multiprocessing's spawn re-launches
    # the frozen exe and can recurse into main() (a fork bomb of Streamlit
    # servers). A daemon thread runs the server in-process and avoids that
    # entirely; Streamlit only installs signal handlers on the main thread,
    # so running its server off-thread is safe.
    server = threading.Thread(target=_run_streamlit, args=(port,), daemon=True)
    server.start()

    # Wait for Streamlit to become ready
    if not _wait_for_server(port):
        print("ERROR: Streamlit server did not start within 30 seconds.", file=sys.stderr)
        sys.exit(1)

    # Open native window via pywebview
    import webview  # type: ignore[import-untyped]

    webview.create_window(
        title="Azure Visio AI Assistant",
        url=url,
        width=1400,
        height=900,
        min_size=(1024, 700),
        text_select=True,
    )
    # webview.start() blocks until the window is closed; the daemon thread
    # (and its Streamlit server) is torn down automatically on exit.
    webview.start(private_mode=False)


if __name__ == "__main__":
    # Harmless no-op for normal runs; required so any accidental child
    # process started by a dependency does not re-run the app.
    multiprocessing.freeze_support()

    # When packaged, the MCP client launches *this same exe* to host the MCP
    # server over stdio (the frozen bootloader can't run "python -m
    # visio_mcp.server"). The VISIO_MCP_SERVER_CHILD flag selects that mode so
    # the child speaks clean JSONRPC on stdout instead of starting the UI.
    if os.environ.get("VISIO_MCP_SERVER_CHILD") == "1":
        if getattr(sys, "frozen", False):
            sys.path.insert(0, str(Path(getattr(sys, "_MEIPASS"))))
        from visio_mcp.server import main as _server_main

        _server_main()
        sys.exit(0)

    main()
