"""
Interactive AI App for Azure Visio Diagram Creation
====================================================
Streamlit-based chat interface that connects to the Visio MCP server,
uses OpenAI/Azure OpenAI for natural language understanding, and renders
live diagram previews.

Run:  streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import streamlit as st

# Ensure the project root is on the path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

from app.mcp_client import VisioMCPClient
from app.ai_agent import AIAgent
from app.diagram_preview import render_diagram_svg, render_diagram_html

# ── Page config ───────────────────────────────────────────────────

st.set_page_config(
    page_title="Azure Visio AI Assistant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────

st.markdown("""
<style>
    .stChatMessage { max-width: 100%; }
    .tool-call {
        background: #f0f4ff;
        border-left: 3px solid #0078D4;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.85em;
        font-family: 'Cascadia Code', 'Consolas', monospace;
    }
    .tool-result {
        background: #f0fff4;
        border-left: 3px solid #107C10;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.82em;
    }
    .validation-score {
        font-size: 2.2em;
        font-weight: 700;
        text-align: center;
        padding: 10px;
    }
    .sidebar-section {
        padding: 6px 0;
        border-bottom: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


# ── Async helper (only for AI agent which is still async) ─────────

def run_async(coro):
    """Run an async coroutine from synchronous Streamlit context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(lambda: asyncio.run(coro)).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ── Session state initialization ─────────────────────────────────

def init_session():
    """Initialize Streamlit session state keys for messages, MCP client, AI agent, and diagram state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mcp_client" not in st.session_state:
        st.session_state.mcp_client = None
    if "ai_agent" not in st.session_state:
        st.session_state.ai_agent = None
    if "onboarding_dismissed" not in st.session_state:
        st.session_state.onboarding_dismissed = False
    if "diagram_state" not in st.session_state:
        st.session_state.diagram_state = None
    if "diagram_rev" not in st.session_state:
        st.session_state.diagram_rev = 0
    if "tool_log" not in st.session_state:
        st.session_state.tool_log = []
    if "connected" not in st.session_state:
        st.session_state.connected = False


init_session()


# ── First-time onboarding ─────────────────────────────────────────

_ONBOARDING_CONTENT = """
### What is this?
A conversational AI assistant that creates **Microsoft Visio** and **draw.io** architecture
diagrams following [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/)
standards — official icons, reference architectures, WAF & CAF validation.

---

### 🚀 Quick Start (3 steps)

**1. Just describe what you need** — type in the chat:
> *"Create a 3-tier web app with App Service, SQL Database, and Redis Cache"*

**2. Or start from a template** — use **Reference Architectures** in the sidebar:
- Baseline Foundry Chat · Azure Landing Zone · Baseline Web App · AI Landing Zone · Microservices on AKS

**3. Save your diagram** — pick **.vsdx** (Visio) or **.drawio** format at the bottom of the sidebar.

---

### 💬 Example Prompts
| What you say | What happens |
|---|---|
| *"Build a hub-spoke network with Azure Firewall"* | Creates full landing zone diagram |
| *"Add an Azure SQL Database connected to the App Service"* | Adds resource + connection |
| *"Validate my architecture against WAF"* | Runs Well-Architected Framework checks |
| *"Validate CAF naming conventions"* | Checks Cloud Adoption Framework compliance |
| *"Import my existing Visio file"* | Upload .vsdx in the sidebar |
| *"Convert this whiteboard photo to a diagram"* | Upload image → AI identifies components |

---

### 🧰 Available Tools
| Category | Tools |
|---|---|
| **Diagram** | Create, save, import Visio/image, auto-layout |
| **Resources** | 123 Azure shapes with official SVG icons |
| **Reference Archs** | 5 buildable templates + 206-entry catalog |
| **Validation** | WAF (6 pillars) + CAF (naming, tagging, structure) |
| **Architecture** | 6 styles, 36 design patterns, catalog search |

---

### 🔑 AI Configuration
The sidebar lets you choose **GitHub Copilot** (auto-detected from `gh auth login`),
**OpenAI**, or **Azure OpenAI** as the AI backend.
"""


# ── Connection management ────────────────────────────────────────

def ensure_connection():
    """Connect to MCP server if not already connected. Returns True on success, False on failure."""
    if not st.session_state.connected:
        with st.spinner("Connecting to Visio MCP server..."):
            try:
                client = VisioMCPClient()
                client.connect()  # blocking — runs MCP in background thread
                st.session_state.mcp_client = client
                st.session_state.ai_agent = AIAgent(client)
                st.session_state.connected = True
            except Exception as e:
                st.error(f"Failed to connect to MCP server: {e}")
                return False
    return True


def refresh_diagram_state():
    """Fetch current diagram state from MCP server and increment the revision counter for SVG re-render."""
    if st.session_state.mcp_client and st.session_state.connected:
        try:
            state = st.session_state.mcp_client.call_tool("get_diagram_state", {})
            st.session_state.diagram_state = state
            st.session_state.diagram_rev += 1
        except Exception:
            pass


# ── GitHub CLI auth helper ────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def _get_gh_token() -> str | None:
    """Try to get a GitHub token from the GitHub CLI (`gh auth token`).

    Returns the token string or None if gh is not installed / not logged in.
    Cached for 5 minutes to avoid repeated subprocess calls.
    """
    import subprocess
    import shutil

    gh_path = shutil.which("gh")
    if not gh_path:
        return None
    try:
        result = subprocess.run(
            [gh_path, "auth", "token"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


# ── Auto-connect on startup ──────────────────────────────────────

# If GitHub CLI auth is available, pre-set the token so auto-connect picks it up
_auto_gh = _get_gh_token()
if _auto_gh and not os.environ.get("OPENAI_API_KEY") and not os.environ.get("AZURE_OPENAI_ENDPOINT"):
    os.environ.setdefault("GITHUB_TOKEN", _auto_gh)

ensure_connection()

# ── Sidebar ──────────────────────────────────────────────────────

with st.sidebar:
    st.title("🏗️ Azure Visio AI")
    st.caption("Interactive architecture diagram assistant")

    with st.expander("❓ How to Use", expanded=not st.session_state.onboarding_dismissed):
        st.markdown(_ONBOARDING_CONTENT)
        if not st.session_state.onboarding_dismissed:
            if st.button("Got it!", type="primary", use_container_width=True, key="btn_dismiss_onboarding"):
                st.session_state.onboarding_dismissed = True
                st.rerun()

    # Connection status
    if st.session_state.connected:
        st.success("Connected to MCP Server", icon="✅")
        tools = st.session_state.mcp_client.tools if st.session_state.mcp_client else []
        st.caption(f"{len(tools)} tools available")
    else:
        if st.button("🔌 Connect to MCP Server", use_container_width=True):
            ensure_connection()
            st.rerun()
        st.warning("Not connected", icon="⚠️")

    st.divider()

    # API key config
    _has_key = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("OPENAI_API_KEY") or os.environ.get("AZURE_OPENAI_ENDPOINT"))
    with st.expander("🔑 AI Configuration", expanded=not _has_key):
        provider = st.radio("Provider", ["GitHub Copilot", "OpenAI", "Azure OpenAI"], horizontal=True)

        if provider == "GitHub Copilot":
            # Auto-detect GitHub CLI auth
            _gh_auto = _get_gh_token()
            if _gh_auto:
                st.success("Authenticated via GitHub CLI (`gh auth`)", icon="✅")
                _gh_display = _gh_auto[:4] + "•" * 12 + _gh_auto[-4:]
                st.caption(f"Token: `{_gh_display}`")
            else:
                st.info("Install [GitHub CLI](https://cli.github.com) and run `gh auth login` to auto-authenticate, or enter a token below.")

            gh_token_manual = st.text_input(
                "Token override (optional)", type="password",
                value="",
                help="Leave blank to use GitHub CLI auth. Or paste a PAT with `copilot` scope.",
            )
            gh_token = gh_token_manual or _gh_auto or ""

            gh_model = st.selectbox(
                "Model",
                [
                    "gpt-4.1",
                    "gpt-4.1-mini",
                    "gpt-4.1-nano",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "o4-mini",
                    "o3-mini",
                    "AI21-Jamba-1.5-Large",
                    "AI21-Jamba-1.5-Mini",
                    "Codestral-2501",
                    "Cohere-command-r",
                    "Cohere-command-r-08-2024",
                    "Cohere-command-r-plus",
                    "Cohere-command-r-plus-08-2024",
                    "DeepSeek-R1",
                    "DeepSeek-V3",
                    "Llama-3.3-70B-Instruct",
                    "MAI-DS-R1",
                    "Ministral-3B",
                    "Mistral-Large-2",
                    "Mistral-Large-2411",
                    "Mistral-Nemo",
                    "Mistral-Small",
                    "Phi-3.5-MoE-instruct",
                    "Phi-3.5-mini-instruct",
                    "Phi-3.5-vision-instruct",
                    "Phi-4",
                    "Phi-4-mini",
                    "Phi-4-multimodal",
                ],
                index=0,
                help="Full list from GitHub Models marketplace",
            )
            if gh_token:
                os.environ["GITHUB_TOKEN"] = gh_token
                os.environ["GITHUB_MODELS_MODEL"] = gh_model
                # Clear other providers so the agent picks GitHub
                os.environ.pop("OPENAI_API_KEY", None)
                os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
            elif not _gh_auto:
                st.warning("No GitHub auth found. Run `gh auth login` or enter a token.")
            st.caption("Uses [GitHub Models](https://github.com/marketplace/models) inference endpoint.")
            st.caption(f"Endpoint: `models.inference.ai.azure.com` · Model: `{gh_model}`")

        elif provider == "OpenAI":
            api_key = st.text_input("OpenAI API Key", type="password",
                                    value=os.environ.get("OPENAI_API_KEY", ""))
            model = st.text_input("Model", value=os.environ.get("OPENAI_MODEL", "gpt-4o"))
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
                os.environ["OPENAI_MODEL"] = model
                os.environ.pop("GITHUB_TOKEN", None)
                os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        else:
            endpoint = st.text_input("Azure Endpoint",
                                     value=os.environ.get("AZURE_OPENAI_ENDPOINT", ""))
            az_key = st.text_input("Azure API Key", type="password",
                                   value=os.environ.get("AZURE_OPENAI_API_KEY", ""))
            deployment = st.text_input("Deployment",
                                       value=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"))
            if endpoint:
                os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
                os.environ.pop("GITHUB_TOKEN", None)
                os.environ.pop("OPENAI_API_KEY", None)
            if az_key:
                os.environ["AZURE_OPENAI_API_KEY"] = az_key
            if deployment:
                os.environ["AZURE_OPENAI_DEPLOYMENT"] = deployment

    st.divider()

    # Quick actions
    st.subheader("Quick Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 New Diagram", use_container_width=True):
            if ensure_connection():
                result = st.session_state.mcp_client.call_tool(
                    "create_diagram", {"name": "Azure Architecture"}
                )
                assistant_msg = f"Created new diagram: **{result.get('name', 'Azure Architecture')}**"
                st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
                if "ai_agent" in st.session_state and hasattr(st.session_state.ai_agent, "inject_context"):
                    st.session_state.ai_agent.inject_context(
                        "Create a new empty Azure architecture diagram.",
                        assistant_msg,
                    )
                refresh_diagram_state()
                st.rerun()

    with col2:
        if st.button("🔍 Validate WAF", use_container_width=True):
            if ensure_connection():
                result = st.session_state.mcp_client.call_tool(
                    "validate_waf", {}
                )
                score = result.get("score", 0)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**WAF Validation Score: {score}/100**\n\n{result.get('summary', '')}\n\n"
                               + "\n".join(f"- **{f['severity']}** [{f.get('pillar', '')}]: {f['message']}"
                                           for f in result.get("findings", [])[:5])
                })
                st.rerun()

    # Reference architectures
    st.subheader("Reference Architectures")
    arch_options = {
        "Baseline Foundry Chat": "baseline_foundry_chat",
        "Azure Landing Zone": "azure_landing_zone",
        "Baseline Web App": "baseline_web_app",
        "AI Landing Zone": "ai_landing_zone",
        "Microservices on AKS": "microservices_aks",
    }
    selected_arch = st.selectbox("Template", list(arch_options.keys()))
    if st.button("Apply Template", use_container_width=True):
        if ensure_connection():
            key = arch_options[selected_arch]
            with st.spinner(f"Building {selected_arch}..."):
                result = st.session_state.mcp_client.call_tool(
                    "apply_reference_architecture",
                    {"architecture_key": key}
                )
            msg = (f"Applied **{selected_arch}** reference architecture.\n\n"
                   f"- {result.get('resource_count', 0)} resources\n"
                   f"- {result.get('connection_count', 0)} connections\n"
                   f"- {result.get('boundary_count', 0)} boundaries\n\n")
            steps = result.get("workflow_steps", [])
            if steps:
                msg += "**Workflow:**\n" + "\n".join(
                    f"{s['step']}. {s['description']}" for s in steps
                )
            st.session_state.messages.append({"role": "assistant", "content": msg})
            # Inject into AI agent so it knows which template was applied
            if "ai_agent" in st.session_state and hasattr(st.session_state.ai_agent, "inject_context"):
                try:
                    state = st.session_state.mcp_client.call_tool("get_diagram_state", {})
                    res_dict = state.get("resources", {})
                    resource_list = [f"{r['name']} ({r['type']})"
                                     for r in (res_dict.values() if isinstance(res_dict, dict) else res_dict)]
                    bnd_dict = state.get("boundaries", {})
                    boundary_list = [f"{b['name']} ({b['type']})"
                                     for b in (bnd_dict.values() if isinstance(bnd_dict, dict) else bnd_dict)]
                    context_detail = msg
                    if resource_list:
                        context_detail += "\n\n**Resources now in diagram:** " + ", ".join(resource_list)
                    if boundary_list:
                        context_detail += "\n\n**Boundaries:** " + ", ".join(boundary_list)
                except Exception:
                    context_detail = msg
                st.session_state.ai_agent.inject_context(
                    f"Apply the {selected_arch} reference architecture template.",
                    context_detail,
                )
            refresh_diagram_state()
            st.rerun()

    st.divider()

    # ── Architecture Catalog (206 entries) ────────────────────────
    with st.expander("📚 Architecture Catalog (206)", expanded=False):
        st.caption("Browse all reference architectures from [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/browse/)")

        _cat_options = [
            "All Categories",
            "AI + Machine Learning",
            "Analytics",
            "Compute",
            "Containers",
            "Databases",
            "DevOps",
            "Developer Tools",
            "Hybrid + Multicloud",
            "Identity",
            "Integration",
            "Internet of Things",
            "Media",
            "Migration",
            "Networking",
            "Security",
            "Storage",
            "Web",
        ]
        _type_options = ["All Types", "Architecture", "Reference Architecture", "Solution Idea", "Best Practice"]

        cat_filter = st.selectbox("Category", _cat_options, key="catalog_cat")
        type_filter = st.selectbox("Type", _type_options, key="catalog_type")
        search_query = st.text_input("🔍 Search", key="catalog_search", placeholder="e.g. kubernetes, machine learning")

        if ensure_connection():
            if search_query:
                catalog_results = st.session_state.mcp_client.call_tool(
                    "search_arch_catalog", {"query": search_query}
                )
                entries = catalog_results.get("results", [])
            else:
                catalog_results = st.session_state.mcp_client.call_tool(
                    "browse_architecture_catalog",
                    {
                        "category": None if cat_filter == "All Categories" else cat_filter,
                        "entry_type": None if type_filter == "All Types" else type_filter,
                    },
                )
                entries = catalog_results.get("entries", [])

            st.caption(f"Showing {len(entries)} of 206 entries")

            for entry in entries[:25]:
                etype = entry.get("type", "")
                badge = {"Architecture": "🏛️", "Reference Architecture": "📐", "Solution Idea": "💡", "Best Practice": "✅"}.get(etype, "📄")
                with st.container():
                    st.markdown(f"**{badge} [{entry['name']}]({entry.get('source_url', '#')})**")
                    st.caption(f"{etype} · {', '.join(entry.get('categories', [])[:2])}")
                    summary = entry.get("summary", "")
                    if summary:
                        st.markdown(f"<small>{summary[:150]}{'...' if len(summary) > 150 else ''}</small>", unsafe_allow_html=True)

            if len(entries) > 25:
                st.info(f"Showing first 25 of {len(entries)} results. Refine your search or filters.")

    st.divider()

    # ── Import section ────────────────────────────────────────────
    st.subheader("Import")

    import_tab1, import_tab2 = st.tabs(["📄 Visio (.vsdx)", "🖼️ Image"])

    with import_tab1:
        uploaded_vsdx = st.file_uploader(
            "Upload existing .vsdx",
            type=["vsdx", "vsd"],
            key="vsdx_upload",
            help="Import an existing Visio diagram — shapes are matched to Azure resources, then WAF/CAF assessed.",
        )
        if uploaded_vsdx:
            vsdx_page_option = st.radio(
                "Pages to import",
                ["All pages", "Specific page"],
                horizontal=True,
                key="vsdx_page_option",
            )
            vsdx_page_num = None
            if vsdx_page_option == "Specific page":
                vsdx_page_num = st.number_input(
                    "Page number (1-based)", min_value=1, value=1, step=1, key="vsdx_page_num"
                )
        vsdx_assess = st.checkbox("Run WAF/CAF assessment", value=True, key="vsdx_assess")
        if uploaded_vsdx and st.button("Import .vsdx", use_container_width=True, key="btn_import_vsdx"):
            if ensure_connection():
                # Save uploaded file to temp location
                import tempfile
                tmp_dir = Path(tempfile.gettempdir()) / "visio_import"
                tmp_dir.mkdir(exist_ok=True)
                tmp_path = tmp_dir / uploaded_vsdx.name
                tmp_path.write_bytes(uploaded_vsdx.getvalue())

                page_arg: int | str = "all"
                if vsdx_page_option == "Specific page" and vsdx_page_num:
                    page_arg = int(vsdx_page_num)

                with st.spinner(f"Importing {uploaded_vsdx.name} (Visio COM parsing)..."):
                    result = st.session_state.mcp_client.call_tool(
                        "import_vsdx",
                        {
                            "file_path": str(tmp_path),
                            "page": page_arg,
                            "assess_waf": vsdx_assess,
                            "assess_caf": vsdx_assess,
                        },
                        timeout=300,
                    )

                if result.get("status") == "imported":
                    page_info = ""
                    pages_imported = result.get("pages_imported", 1)
                    page_names = result.get("page_names", [])
                    if pages_imported > 1:
                        page_info = f"- {pages_imported} pages: {', '.join(page_names)}\n"
                    elif page_names:
                        page_info = f"- Page: {page_names[0]}\n"
                    msg_parts = [
                        f"**Imported** `{uploaded_vsdx.name}` as **{result.get('name', 'Diagram')}**",
                        page_info + f"- {result.get('resources_imported', 0)} resources",
                        f"- {result.get('boundaries_imported', 0)} boundaries",
                        f"- {result.get('connections_imported', 0)} connections",
                    ]
                    unmatched = result.get("unmatched_resources", [])
                    if unmatched:
                        msg_parts.append(f"- ⚠️ {len(unmatched)} unmatched: {', '.join(unmatched[:5])}")

                    waf = result.get("waf_assessment")
                    if waf:
                        msg_parts.append(f"\n**WAF Score: {waf['score']}/100** ({waf['findings_count']} findings)")
                        for f in waf.get("top_findings", [])[:3]:
                            msg_parts.append(f"  - **{f['severity']}** [{f['pillar']}]: {f['message']}")

                    caf = result.get("caf_assessment")
                    if caf:
                        msg_parts.append(f"\n**CAF Score: {caf['score']}/100** ({caf['findings_count']} findings)")
                        for f in caf.get("top_findings", [])[:3]:
                            msg_parts.append(f"  - **{f['severity']}** [{f['pillar']}]: {f['message']}")

                    msg_parts.append("\nYou can now ask me to improve this architecture, add resources, or re-validate.")
                    vsdx_msg = "\n".join(msg_parts)
                    st.session_state.messages.append({"role": "assistant", "content": vsdx_msg})
                    if "ai_agent" in st.session_state and hasattr(st.session_state.ai_agent, "inject_context"):
                        st.session_state.ai_agent.inject_context(
                            f"Import existing Visio file {uploaded_vsdx.name} into the diagram.",
                            vsdx_msg,
                        )
                    refresh_diagram_state()
                    st.rerun()
                else:
                    st.error(result.get("message", "Import failed"))

    with import_tab2:
        uploaded_img = st.file_uploader(
            "Upload diagram image",
            type=["png", "jpg", "jpeg", "bmp", "gif", "webp", "tif", "tiff", "svg"],
            key="img_upload",
            help="Upload a screenshot, whiteboard photo, block diagram, or SVG — AI identifies components and creates a proper Azure diagram.",
        )
        if uploaded_img:
            if uploaded_img.name.lower().endswith(".svg"):
                # st.image doesn't render SVG well; use raw HTML
                svg_bytes = uploaded_img.getvalue()
                st.markdown(
                    f'<div style="max-height:200px;overflow:auto;border:1px solid #555;border-radius:4px;padding:4px">'
                    f'{svg_bytes.decode("utf-8", errors="replace")}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.image(uploaded_img, caption="Preview", use_container_width=True)

        if uploaded_img and st.button("Convert to Diagram", use_container_width=True, key="btn_import_img"):
            if ensure_connection():
                import tempfile
                tmp_dir = Path(tempfile.gettempdir()) / "visio_import"
                tmp_dir.mkdir(exist_ok=True)
                tmp_path = tmp_dir / uploaded_img.name
                tmp_path.write_bytes(uploaded_img.getvalue())

                is_svg = uploaded_img.name.lower().endswith(".svg")
                spinner_text = "Analyzing SVG structure with AI..." if is_svg else "Analyzing image with AI vision model..."
                with st.spinner(spinner_text):
                    result = st.session_state.mcp_client.call_tool(
                        "import_image",
                        {"file_path": str(tmp_path)},
                        timeout=120,
                    )

                if result.get("status") == "imported":
                    msg_parts = [
                        f"**Converted** `{uploaded_img.name}` → **{result.get('name', 'Diagram')}**",
                        f"- {result.get('resources_created', 0)} resources identified",
                        f"- {result.get('boundaries_created', 0)} boundaries identified",
                        f"- {result.get('connections_created', 0)} connections identified",
                        f"- Analysis: `{result.get('analysis_method', 'vision')}` via `{result.get('vision_model', 'unknown')}`",
                        "\nYou can now ask me to refine, add resources, validate WAF/CAF, or save as .vsdx.",
                    ]
                    img_msg = "\n".join(msg_parts)
                    st.session_state.messages.append({"role": "assistant", "content": img_msg})
                    if "ai_agent" in st.session_state and hasattr(st.session_state.ai_agent, "inject_context"):
                        st.session_state.ai_agent.inject_context(
                            f"Convert the uploaded image {uploaded_img.name} to an Azure architecture diagram.",
                            img_msg,
                        )
                    refresh_diagram_state()
                    st.rerun()
                else:
                    st.error(result.get("message", "Image conversion failed"))

    st.divider()

    # Diagram info
    if st.session_state.diagram_state:
        ds = st.session_state.diagram_state
        st.subheader("Current Diagram")
        st.caption(ds.get("name", "Untitled"))

        resources = ds.get("resources", {})
        connections = ds.get("connections", {})
        boundaries = ds.get("boundaries", {})

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Resources", len(resources))
        mc2.metric("Connections", len(connections))
        mc3.metric("Boundaries", len(boundaries))

        if resources:
            with st.expander("Resources", expanded=False):
                for rid, r in (resources.items() if isinstance(resources, dict) else []):
                    rname = r.get("display_name", r.get("name", rid)) if isinstance(r, dict) else getattr(r, "display_name", rid)
                    rtype = r.get("resource_type", r.get("type", "")) if isinstance(r, dict) else getattr(r, "resource_type", "")
                    st.text(f"• {rname} ({rtype})")

    # Save button
    st.divider()
    _default_save = str(_ROOT / "output" / "diagram.vsdx")
    if "save_path" not in st.session_state:
        st.session_state.save_path = _default_save
    if "save_format" not in st.session_state:
        st.session_state.save_format = "Visio (.vsdx)"

    # Format selector
    save_format = st.radio(
        "Output format",
        ["Visio (.vsdx)", "draw.io (.drawio)"],
        index=0 if st.session_state.save_format == "Visio (.vsdx)" else 1,
        horizontal=True,
        key="save_format_radio",
    )
    st.session_state.save_format = save_format

    # Update default extension when format changes
    _fmt_ext = ".vsdx" if "vsdx" in save_format else ".drawio"
    _current_path = Path(st.session_state.save_path)
    if _current_path.suffix.lower() not in (".vsdx", ".drawio"):
        st.session_state.save_path = str(_current_path.with_suffix(_fmt_ext))
    elif _current_path.suffix.lower() != _fmt_ext:
        st.session_state.save_path = str(_current_path.with_suffix(_fmt_ext))

    save_col1, save_col2 = st.columns([4, 1])
    with save_col1:
        save_path = st.text_input("Save path", value=st.session_state.save_path, key="save_path_input")
        st.session_state.save_path = save_path
    with save_col2:
        st.markdown("<div style='margin-top:1.65rem'></div>", unsafe_allow_html=True)
        if st.button("📂", key="browse_btn", help="Browse for save location"):
            st.session_state["_browse_pending"] = True
            st.rerun()

    # Handle browse dialog in a separate step to avoid blocking page load
    if st.session_state.get("_browse_pending"):
        st.session_state["_browse_pending"] = False
        import subprocess as _sp
        _init_dir = str(Path(st.session_state.save_path).parent)
        _init_file = Path(st.session_state.save_path).name
        _filter_str = (
            'Visio files (*.vsdx)|*.vsdx|All files (*.*)|*.*'
            if "vsdx" in save_format
            else 'draw.io files (*.drawio)|*.drawio|All files (*.*)|*.*'
        )
        # WinForms dialog via PowerShell with -STA to avoid threading issues
        _ps_script = (
            "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; "
            "$f = New-Object System.Windows.Forms.SaveFileDialog; "
            "$f.Title = 'Save Diagram'; "
            f"$f.Filter = '{_filter_str}'; "
            f"$f.InitialDirectory = '{_init_dir}'; "
            f"$f.FileName = '{_init_file}'; "
            "$f.OverwritePrompt = $true; "
            "if ($f.ShowDialog() -eq 'OK') { Write-Output $f.FileName }"
        )
        try:
            _result = _sp.run(
                ["powershell", "-NoProfile", "-STA", "-Command", _ps_script],
                capture_output=True, text=True, timeout=120,
            )
            _chosen = _result.stdout.strip()
            if _chosen:
                st.session_state.save_path = _chosen
                st.rerun()
            else:
                st.info("Browse cancelled.")
        except Exception as e:
            st.warning(f"Browse dialog failed: {e}")

    _save_label = "💾 Save as .vsdx" if "vsdx" in save_format else "💾 Save as .drawio"
    if st.button(_save_label, use_container_width=True):
        if ensure_connection():
            _fmt_key = "vsdx" if "vsdx" in save_format else "drawio"
            # Ensure output directory exists
            save_path = st.session_state.save_path
            save_dir = Path(save_path).parent
            save_dir.mkdir(parents=True, exist_ok=True)
            _spinner_msg = (
                "Saving diagram (Visio rendering may take a moment)..."
                if _fmt_key == "vsdx"
                else "Saving diagram as draw.io..."
            )
            with st.spinner(_spinner_msg):
                try:
                    result = st.session_state.mcp_client.call_tool(
                        "save_diagram", {"output_path": save_path, "format": _fmt_key}, timeout=300
                    )
                except TimeoutError:
                    st.error("Save timed out — try again.")
                    result = None
                except Exception as e:
                    st.error(f"Save failed: {e}")
                    result = None
            if result and result.get("status") == "saved":
                saved_to = result.get('output_path', save_path)
                st.success(f"Saved to {saved_to}")
                if os.path.isfile(saved_to):
                    file_size = os.path.getsize(saved_to)
                    st.caption(f"File size: {file_size / 1024:.1f} KB")
                else:
                    st.warning("File not found at reported path.")
            elif result:
                st.error(result.get("message", "Save failed"))

    # Reset
    if st.button("🗑️ Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.ai_agent:
            st.session_state.ai_agent.reset_conversation()
        st.session_state.diagram_state = None
        st.session_state.diagram_rev = 0
        st.session_state.tool_log = []
        st.rerun()


# ── Main area ────────────────────────────────────────────────────

# Two-column layout: chat + diagram preview
chat_col, preview_col = st.columns([3, 2])

with preview_col:
    st.subheader("Diagram Preview")
    if st.session_state.diagram_state:
        preview_html = render_diagram_html(st.session_state.diagram_state)
        import streamlit.components.v1 as components
        # Embed revision marker so Streamlit detects content change and re-renders
        html_with_rev = f"<!-- rev {st.session_state.diagram_rev} -->\n{preview_html}"
        components.html(html_with_rev, height=780, scrolling=True)
    else:
        st.info("No diagram yet. Start by creating one or applying a reference architecture.")

    # Tool call log
    if st.session_state.tool_log:
        with st.expander(f"Tool Call Log ({len(st.session_state.tool_log)} calls)", expanded=False):
            for entry in st.session_state.tool_log[-20:]:
                st.markdown(
                    f'<div class="tool-call">🔧 <b>{entry["tool"]}</b>'
                    f'({json.dumps(entry.get("args", {}), separators=(",", ":"))})</div>',
                    unsafe_allow_html=True,
                )
                result_preview = json.dumps(entry.get("result", {}), indent=2)
                if len(result_preview) > 300:
                    result_preview = result_preview[:300] + "..."
                st.markdown(
                    f'<div class="tool-result">✅ {result_preview}</div>',
                    unsafe_allow_html=True,
                )


with chat_col:
    st.subheader("Chat")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Welcome message
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("""Welcome! I can help you create Azure architecture diagrams in Visio.

**Try these:**
- *"Create a 3-tier web application architecture"*
- *"Build a hub-spoke landing zone with Azure Firewall"*
- *"Apply the baseline Foundry chat reference architecture"*
- *"Add an Azure SQL Database and connect it to the App Service"*
- *"Validate my architecture against WAF"*

GitHub Copilot auth is auto-detected from `gh auth login`.
""")

    # Chat input
    if prompt := st.chat_input("Describe your Azure architecture..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Ensure connected
        if not ensure_connection():
            st.stop()

        # Process with AI agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply, tool_log = run_async(
                        st.session_state.ai_agent.chat(prompt)
                    )
                    st.session_state.tool_log.extend(tool_log)

                    # Show tool calls inline
                    if tool_log:
                        with st.expander(f"🔧 {len(tool_log)} tool calls", expanded=False):
                            for entry in tool_log:
                                st.code(f"{entry['tool']}({json.dumps(entry.get('args', {}), indent=2)})",
                                        language="json")

                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

                    # Refresh diagram preview
                    refresh_diagram_state()

                except ValueError as e:
                    error_msg = str(e)
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})
                except Exception as e:
                    error_msg = f"Error: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})

        st.rerun()
