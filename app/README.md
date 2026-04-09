# app/ — Interactive Streamlit UI

A Streamlit-based chat interface that connects to the Visio MCP server, uses AI for natural language understanding, and provides live diagram previews.

## Files

| File | Lines | Purpose |
|------|------:|---------|
| [`streamlit_app.py`](streamlit_app.py) | 578 | Main app — chat interface, sidebar, diagram preview, import UI |
| [`ai_agent.py`](ai_agent.py) | 253 | AI agent — OpenAI function calling, token management, conversation truncation |
| [`diagram_preview.py`](diagram_preview.py) | 251 | Browser-side SVG renderer — converts DiagramState to inline SVG preview |
| [`mcp_client.py`](mcp_client.py) | 154 | Thread-safe MCP client — stdio transport, background asyncio event loop |
| [`run.py`](run.py) | 13 | CLI launcher — `visio-app` entry point |
| [`.env.example`](.env.example) | 15 | Environment variable template for all 3 AI providers |
| [`__init__.py`](__init__.py) | 1 | Package marker |

## Running

```powershell
# Recommended: with GitHub Copilot auto-auth
$env:GITHUB_TOKEN = (gh auth token)
.\.venv\Scripts\streamlit.exe run app/streamlit_app.py --server.port 8501 --server.headless true
```

Or via the entry point:
```powershell
visio-app
```

The app auto-connects to the MCP server on startup (spawns `python -m visio_mcp.server` as a subprocess via stdio).

## App Layout

```
┌─────────────── Sidebar ───────────────┬──────────── Main Area ─────────────┐
│ 🏗️ Azure Visio AI                     │                                    │
│ ✅ Connected to MCP Server            │  ┌─ Chat (3/5) ──┬─ Preview (2/5)─┐│
│                                       │  │               │                ││
│ 🔑 AI Configuration                  │  │  User: ...    │  [SVG Diagram] ││
│   Provider: GitHub Copilot / OpenAI   │  │  Assistant:.. │                ││
│   Model: gpt-4.1                      │  │               │  Tool Call Log ││
│                                       │  │  [Chat Input] │                ││
│ Quick Actions                         │  └───────────────┴────────────────┘│
│   [📊 New Diagram] [🔍 Validate WAF] │                                    │
│                                       │                                    │
│ Reference Architectures               │                                    │
│   [Template ▾] [Apply Template]       │                                    │
│                                       │                                    │
│ Import                                │                                    │
│   📄 Visio (.vsdx) │ 🖼️ Image        │                                    │
│   [Upload] [Import .vsdx]             │                                    │
│                                       │                                    │
│ Current Diagram                       │                                    │
│   Resources: 27  Connections: 15      │                                    │
│                                       │                                    │
│ Save path: output/diagram.vsdx [📂]   │                                    │
│ [💾 Save as .vsdx]                    │                                    │
│ [🗑️ Reset Conversation]              │                                    │
└───────────────────────────────────────┴────────────────────────────────────┘
```

## AI Agent (ai_agent.py)

### Provider Priority

1. **`GITHUB_TOKEN`** → GitHub Models endpoint (`models.inference.ai.azure.com`)
2. **`AZURE_OPENAI_ENDPOINT`** + `AZURE_OPENAI_API_KEY` → Azure OpenAI
3. **`OPENAI_API_KEY`** → OpenAI

The agent auto-detects environment variable changes and recreates the client.

### Token Management

- **Max conversation**: ~40,000 characters (~10K tokens)
- **Max tool result**: 1,500 characters (truncated with notice)
- **Conversation truncation**: Keeps system prompt + most recent messages; groups assistant `tool_calls` + tool responses atomically so they're never orphaned
- **Schema compaction**: Strips tool descriptions to first sentence, removes parameter descriptions

### Sidebar Context Injection

Sidebar actions (Apply Template, New Diagram, Import VSDX, Convert Image) bypass the chat input but still modify the diagram. To keep the AI aware, each sidebar action calls `agent.inject_context(user_text, assistant_text)` which appends a synthetic user/assistant exchange to the conversation. For template applications, the full resource and boundary list from `get_diagram_state` is included so the AI knows exactly what's loaded.

### Function Calling Loop

```
User prompt → append to conversation → loop (max 15 rounds):
  ├─ Call chat.completions.create(tools=..., tool_choice="auto")
  ├─ If tool_calls: execute each via MCP client, append results
  └─ If no tool_calls: return final text + tool log
```

### System Prompt

The agent is instructed to:
- Break requests into steps: create → boundaries → resources → connect → layout → validate
- Use CAF-aligned naming (e.g., `rg-app-prod-eastus`)
- Always suggest WAF/CAF validation after building
- Suggest reference architectures for common patterns
- Confirm save paths before saving

### Supported Models

Via GitHub Models: `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-4o`, `gpt-4o-mini`, `o4-mini`, `o3-mini`, `DeepSeek-R1`, `DeepSeek-V3`, `Llama-3.3-70B-Instruct`, `Phi-4`, `Phi-4-multimodal`, `Mistral-Large-2`, and 15+ more.

## MCP Client (mcp_client.py)

The `VisioMCPClient` runs the MCP session in a **dedicated background thread** with its own asyncio event loop. This is required because Streamlit's synchronous rerun model conflicts with async context managers.

### Key Design

```python
class VisioMCPClient:
    # Background thread owns the event loop
    _thread: threading.Thread
    _loop: asyncio.AbstractEventLoop
    _session: ClientSession

    def connect(self):       # Blocking — starts background thread, waits for ready
    def call_tool(name, args, timeout=60):  # Thread-safe — submits to background loop
    def get_tools_for_openai():             # Returns tools in OpenAI function calling format
```

### Transport

Uses `StdioServerParameters` to spawn the MCP server as a subprocess:
```python
StdioServerParameters(
    command=".venv/Scripts/python.exe",
    args=["-m", "visio_mcp.server"],
    env={"PYTHONPATH": "src", **os.environ},
)
```

## Diagram Preview (diagram_preview.py)

Renders the diagram state as an inline SVG in the browser using Azure Architecture Center colors. This is a lightweight preview — the actual `.vsdx` rendering is done by the Visio COM engine.

Features:
- Boundary rectangles with type-specific colors
- Resource shapes with Azure brand colors
- Connection lines with arrows
- Step number circles
- Responsive scaling via `viewBox`

## Environment Variables

| Variable | Provider | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | GitHub Copilot | PAT with `copilot` scope, or output of `gh auth token` |
| `GITHUB_MODELS_MODEL` | GitHub Copilot | Model name (default: `gpt-4o`) |
| `OPENAI_API_KEY` | OpenAI | API key |
| `OPENAI_MODEL` | OpenAI | Model name (default: `gpt-4o`) |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI | Endpoint URL |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI | API key |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI | Deployment name |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI | API version (default: `2024-12-01-preview`) |

Only **one** provider needs to be configured. GitHub Copilot is recommended — just run `gh auth login`.
