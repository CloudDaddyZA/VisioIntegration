# app/ — Interactive Streamlit AI Application

The Streamlit-based front end that provides a chat interface, live diagram preview,
and sidebar controls for the Visio Azure MCP server.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Streamlit App (streamlit_app.py)                           │
│ ┌─────────────────┐  ┌────────────────────────────────────┐ │
│ │ Sidebar          │  │ Main Area                          │ │
│ │ • AI Config      │  │ ┌──────────────┐ ┌──────────────┐ │ │
│ │ • Business →     │  │ │ Chat Column  │ │ Preview Col  │ │ │
│ │   Architecture  │  │ │ (3/5 width)  │ │ (2/5 width)  │ │ │
│ │ • Quick Actions  │  │ │              │ │ diagram_     │ │ │
│ │ • Ref Archs      │  │ │ ai_agent.py  │ │ preview.py   │ │ │
│ │ • Arch Catalog   │  │ │   ↕ OpenAI   │ │ (SVG render) │ │ │
│ │   Image)         │  │ │              │ │              │ │ │
│ │ • Diagram Info   │  │ └──────┬───────┘ └──────────────┘ │ │
│ │ • Save / Browse  │  │        │                           │ │
│ └─────────────────┘  └────────┼───────────────────────────┘ │
│                               │                              │
│                    ┌──────────▼─────────┐                    │
│                    │ mcp_client.py      │                    │
│                    │ (stdio transport)  │                    │
│                    └──────────┬─────────┘                    │
│                               │                              │
└───────────────────────────────┼──────────────────────────────┘
                                │ stdin/stdout JSON-RPC
                    ┌───────────▼──────────┐
                    │ visio_mcp.server     │
                    │ (MCP Server – 31     │
                    │  tools, 8 resources, │
                    │  7 prompts)          │
                    └──────────────────────┘
```

---

## Module Reference

### `streamlit_app.py` (~940 lines)

Main application entry point. Manages:

- **Page config & CSS** — Wide layout, Azure-blue accent on tool-call/result callouts
- **Session state** — `messages`, `mcp_client`, `ai_agent`, `diagram_state`, `diagram_rev`, `tool_log`, `biz_req_text`
- **Connection management** — `init_session()`, `ensure_connection()`, `refresh_diagram_state()`
- **GitHub CLI auto-auth** — Detects `gh auth token` and pre-sets `GITHUB_TOKEN`
- **First-run onboarding** — Expandable sidebar guide with quick start (4 steps including business requirements), example prompts, and tool overview
- **Sidebar controls**:
  - AI provider radio (GitHub Copilot / OpenAI / Azure OpenAI) with model picker
  - **Business → Architecture**: Text area for business requirements + "Generate Architecture" button — injects a structured prompt that triggers the AI’s business-to-architecture workflow (analyse → style → catalog → patterns → build → validate → explain)
  - Quick Actions: New Diagram, Validate WAF
  - Reference Architecture dropdown (5 templates)
  - Architecture Catalog expander (206 entries, filterable by category/type/search)
  - Import tabs: Visio `.vsdx` upload (multi-page with page selector), Image upload (PNG/JPG/SVG → AI conversion)
  - Diagram info metrics (resources, connections, boundaries)
  - Output format selector: Visio (`.vsdx`) or draw.io (`.drawio`)
  - Save with file browser dialog (PowerShell WinForms)
- **Main area**: Two-column layout — chat history + tool-call log | HTML/SVG diagram preview with page tabs

### `ai_agent.py` (~400 lines)

Orchestrates AI ↔ MCP tool-calling loop:

- **`AIAgent` class** — Wraps OpenAI function-calling with MCP tool definitions
- **`SYSTEM_PROMPT`** — 18-guideline prompt covering:
  - Step-by-step architecture builds
  - CAF naming conventions
  - WAF/CAF validation reminders
  - Save workflow with path confirmation
  - Reference architecture merging (`merge=True`)
  - Architecture styles (14) and design patterns (50)
  - Extended icons (Fabric, Entra)
  - Architecture Catalog (206 entries)
  - Business requirements → architecture workflow
  - Post-import discovery questions (subscription/RG layout, VNet topology, data flow)
  - Image attachment → boundary restructuring workflow
  - **SKU & sizing recommendations** — calls `get_sku_recommendations`, `query_azure_pricing`, `compare_azure_skus` for live-data-backed guidance
  - **Resource suggestions** — identifies missing WAF/monitoring/security resources
  - **FinOps & compliance** — cost optimization, right-sizing, reserved instances, compliance alignment
- **Provider support** — Automatic client creation for:
  - GitHub Copilot (GitHub Models at `models.inference.ai.azure.com`)
  - Azure OpenAI (with deployment + API version)
  - OpenAI (direct)
- **Token management** — `_compact_tool_schemas()` strips verbose descriptions (preserves
  array `items` for OpenAI schema compliance); `_truncate_conversation()` keeps
  conversation within ~40K chars, preserving atomic tool-call/response message groups
- **`chat()` method** — Multi-round tool-calling loop: sends user message → receives
  tool_calls → executes via MCP → feeds results back → repeats until final text reply

### `mcp_client.py` (~162 lines)

Thread-safe MCP client using stdio transport:

- **`VisioMCPClient` class** — Runs the MCP session in a dedicated background thread
  with its own `asyncio` event loop (avoids Streamlit's sync rerun conflicts)
- **`connect()`** — Spawns `.venv/Scripts/python.exe -m visio_mcp.server` as a subprocess,
  waits for session initialization (30s timeout)
- **`call_tool(name, args)`** — Thread-safe blocking call via `run_coroutine_threadsafe()`
  with configurable timeout (default 120s)
- **`get_tools_for_openai()`** — Formats MCP tool schemas into OpenAI function-calling format

### `diagram_preview.py` (~350 lines)

Client-side SVG/HTML renderer for real-time diagram preview:

- **`render_diagram_svg(state, width, height, page_filter)`** — Converts diagram state dict to SVG markup, with optional page filtering
- **`render_diagram_html(state, width, height)`** — Wraps SVG output in tabbed HTML when multiple pages exist; falls back to plain SVG for single-page diagrams

### `components/` — Custom Streamlit Components

- **`paste_image.py`** — Custom component enabling paste-from-clipboard image input
- **`paste_image_frontend/`** — JavaScript/HTML frontend for the paste component
- **Page tab support** — JavaScript-based tab switching for multi-page Visio imports, with per-page coordinate normalization
- **Color palettes** matching Azure Architecture Center:

  | Element | Colors |
  |---------|--------|
  | Boundaries | `#E5E5E5` subscription, `#DEEAF6` VNet, `#E2F0D9` subnet, `#FFF2CC` AZ, `#E8E0EE` mgmt group |
  | Connectors | `#0078D4` data flow, `#107C10` network, `#7030A0` VPN, `#FF8C00` ExpressRoute |
  | Categories | `#0078D4` Compute, `#107C10` Networking, `#E74856` Databases, `#FFB900` Identity |

- **Helpers** — `_resource_color()` maps types to colors by keyword matching,
  `_initials()` generates 2-char icon placeholders, `_get_area()` sorts boundaries largest-first

---

## Environment Variables

| Variable | Provider | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | GitHub Copilot | Auto-detected from `gh auth token` or set manually |
| `GITHUB_MODELS_MODEL` | GitHub Copilot | Model name (default: `gpt-4o`) |
| `OPENAI_API_KEY` | OpenAI | API key |
| `OPENAI_MODEL` | OpenAI | Model name (default: `gpt-4o`) |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI | Endpoint URL |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI | API key |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI | Deployment name |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI | API version (default: `2024-12-01-preview`) |

---

## Running

```powershell
# Recommended (auto-injects GitHub CLI auth):
$env:GITHUB_TOKEN = (& "C:\Program Files\GitHub CLI\gh.EXE" auth token)
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
.\.venv\Scripts\streamlit.exe run app/streamlit_app.py --server.port 8511 --server.headless true
```

The app auto-connects to the MCP server on startup. No separate server process needed — `mcp_client.py` spawns it as a stdio subprocess.

---

## Dependencies

- `streamlit` — UI framework
- `openai` — AI provider SDK (supports OpenAI, Azure OpenAI, and GitHub Models)
- `mcp` — Model Context Protocol client library
- App modules import from `src/visio_mcp/` via `PYTHONPATH`
