"""MCP client that connects to the Visio Azure MCP server via stdio transport.

Runs the MCP session in a dedicated background thread with its own asyncio
event loop so that Streamlit's synchronous rerun model cannot break the
async context managers.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import logging
import sys
import threading
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

# Resolve paths relative to the workspace root
_WORKSPACE = Path(__file__).resolve().parent.parent
_VENV_PYTHON = _WORKSPACE / ".venv" / "Scripts" / "python.exe"
_SRC_DIR = _WORKSPACE / "src"


class VisioMCPClient:
    """Thread-safe wrapper around the Visio MCP server connection.

    All MCP operations run on a dedicated background thread with its own
    event loop, avoiding the cross-thread async context manager issues
    that occur with Streamlit.
    """

    def __init__(self) -> None:
        self._tools: list[dict[str, Any]] = []
        self._connected = False
        # Dedicated event loop + thread for the MCP session
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._session: ClientSession | None = None
        self._cm = None
        self._ready = threading.Event()
        self._error: Exception | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def tools(self) -> list[dict[str, Any]]:
        return list(self._tools)

    # ── Public (sync) API for Streamlit ──────────────────────────

    def connect(self) -> None:
        """Start the background event loop and connect to the MCP server (blocking)."""
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        # Wait until the session is ready (or failed)
        self._ready.wait(timeout=30)
        if self._error:
            raise self._error

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        timeout: float = 120,
    ) -> dict[str, Any]:
        """Call a tool on the MCP server (blocking, thread-safe).

        Args:
            tool_name: MCP tool name.
            arguments: Tool arguments dict.
            timeout: Max seconds to wait for the result (default 120).
        """
        if not self._loop or not self._connected:
            raise RuntimeError("Not connected. Call connect() first.")
        future = asyncio.run_coroutine_threadsafe(
            self._call_tool_async(tool_name, arguments or {}), self._loop,
        )
        return future.result(timeout=timeout)

    def disconnect(self) -> None:
        """Shut down the background loop and MCP connection."""
        self._connected = False  # signal the loop to stop
        if self._thread:
            self._thread.join(timeout=5)

    # ── Background loop ──────────────────────────────────────────

    def _run_loop(self) -> None:
        """Entry point for the dedicated background thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._session_lifecycle())
        except Exception:
            pass  # clean shutdown
        finally:
            self._loop.close()

    async def _session_lifecycle(self) -> None:
        """Run the MCP session for the lifetime of the background loop."""
        python_exe = str(_VENV_PYTHON) if _VENV_PYTHON.exists() else sys.executable

        # Build env: inherit current environment, overlay PYTHONPATH
        import os as _os
        env = dict(_os.environ)
        env["PYTHONPATH"] = str(_SRC_DIR)

        server_params = StdioServerParameters(
            command=python_exe,
            args=["-m", "visio_mcp.server"],
            cwd=str(_WORKSPACE),
            env=env,
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Discover available tools
                    tools_result = await session.list_tools()
                    self._tools = [
                        {
                            "name": t.name,
                            "description": t.description or "",
                            "parameters": t.inputSchema if hasattr(t, "inputSchema") else {},
                        }
                        for t in tools_result.tools
                    ]
                    self._session = session
                    self._connected = True
                    logger.info("Connected to Visio MCP server with %d tools", len(self._tools))

                    # Signal that we're ready, then keep the loop alive
                    self._ready.set()
                    # Run until the loop is stopped externally
                    while self._connected:
                        await asyncio.sleep(0.1)

        except Exception as exc:
            self._error = exc
            self._ready.set()  # unblock the caller

    async def _call_tool_async(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool on the MCP server (async, runs on the background loop)."""
        if not self._session:
            raise RuntimeError("Session not available.")

        result = await self._session.call_tool(tool_name, arguments)

        if result.content:
            for block in result.content:
                if hasattr(block, "text"):
                    try:
                        return json.loads(block.text)
                    except json.JSONDecodeError:
                        return {"result": block.text}
            return {"result": str(result.content)}
        return {"result": "No content returned"}

    def get_tools_for_openai(self) -> list[dict[str, Any]]:
        """Return tool definitions formatted for OpenAI function calling."""
        openai_tools = []
        for tool in self._tools:
            schema = dict(tool.get("parameters", {}))
            if not schema:
                schema = {"type": "object", "properties": {}}

            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": schema,
                },
            })
        return openai_tools
