"""AI agent that translates natural language into MCP tool calls using OpenAI."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from openai import AsyncAzureOpenAI, AsyncOpenAI

from .mcp_client import VisioMCPClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an Azure architecture diagram assistant. You help users create, modify, \
and validate Microsoft Visio architecture diagrams using the Visio MCP server tools.

You have access to tools that:
- Create diagrams and add Azure resources (VMs, App Services, databases, etc.)
- Add boundaries (VNets, subnets, resource groups)
- Connect resources with labeled arrows
- Apply reference architectures from Microsoft Architecture Center
- Auto-layout diagrams
- Validate against WAF (Well-Architected Framework) and CAF (Cloud Adoption Framework)
- Save diagrams as .vsdx files
- Import existing .vsdx files (parses shapes, runs WAF/CAF assessment, lets you build on top)
- Import images (screenshots, whiteboard photos, block diagrams) and convert them to proper Azure diagrams with correct icons
- Suggest architecture styles and get detailed guidance on Azure Architecture Center patterns

Guidelines:
1. When the user describes an architecture, break it into steps: create diagram → \
add boundaries → add resources → connect them → auto-layout → validate.
2. Use descriptive CAF-aligned names (e.g., 'rg-app-prod-eastus', 'vm-web-prod-001').
3. Always suggest running WAF and CAF validation after building a diagram.
4. For common patterns, suggest using reference architectures first.
5. Explain what you're doing at each step.
6. When multiple resources need to be added, add them one by one.
7. After adding resources and connections, apply auto_layout for clean arrangement.
8. SAVING DIAGRAMS: When the user asks to save, ALWAYS confirm the save path \
before calling save_diagram. Suggest a descriptive filename based on the diagram \
title (e.g., 'ai-landing-zone-prod.vsdx'). Tell the user the full resolved path \
where the file will be saved. Use just the filename — the server resolves it to \
the output/ directory automatically. After saving, VERIFY the tool result status \
and report success or failure clearly — including the actual output_path returned.
9. MERGING ARCHITECTURES: When the diagram already contains resources and the user \
asks to add, combine, or extend with another reference architecture, ALWAYS call \
apply_reference_architecture with merge=True. This adds the new architecture's \
resources into the existing diagram without wiping it. Only use merge=False (or \
omit merge) when starting fresh or when the user explicitly asks to replace the \
current diagram. After merging, suggest connecting the new resources to existing \
ones and re-running auto_layout.
10. ARCHITECTURE STYLES: When the user asks about architecture patterns or describes \
a workload scenario, use suggest_architecture_style to recommend the best-fit pattern \
from the Azure Architecture Center styles: N-Tier, Web-Queue-Worker, Microservices, \
Event-Driven, Big Data, or Big Compute (HPC). Use the returned diagram_conventions \
to guide resource placement and arrow direction. Use get_architecture_style_detail \
for deeper guidance on a specific style.
11. DESIGN PATTERNS: When the user asks about cloud design patterns or describes a \
specific challenge (distributed transactions, caching, resilience, migration, etc.), \
use suggest_design_patterns to recommend patterns from the Azure Architecture Center \
catalog (35+ patterns including CQRS, Event Sourcing, Saga, Circuit Breaker, \
Cache-Aside, Publisher-Subscriber, Retry, Sidecar, Strangler Fig, Throttling, etc.). \
Use the returned diagram_implications to guide how the pattern shapes the architecture \
diagram. Use get_design_pattern_detail for deeper guidance on a specific pattern.
12. EXTENDED ICONS: In addition to Azure Public Service icons, Fabric icons \
(fabric_lakehouse, fabric_data_warehouse, fabric_pipeline, fabric_notebook, \
fabric_eventhouse, fabric_eventstream, fabric_report, fabric_power_bi, fabric_onelake, \
etc.) and Entra icons (entra_id_protection, entra_id_governance, entra_internet_access, \
entra_private_access, entra_verified_id, entra_workload_id) are available as \
resource_type keys.
13. ARCHITECTURE CATALOG: 206 reference architectures and solution ideas extracted from \
Azure Architecture Center (https://learn.microsoft.com/en-us/azure/architecture/browse/). \
Use browse_architecture_catalog to list by category or type. Use search_arch_catalog to \
find architectures by keyword. Use get_arch_catalog_entry to get full details for a \
specific entry. Categories: AI + Machine Learning, Analytics, Compute, Containers, \
Databases, DevOps, Developer Tools, Hybrid + Multicloud, Identity, Integration, IoT, \
Media, Migration, Networking, Security, Storage, Web. Types: Architecture, Reference \
Architecture, Solution Idea, Best Practice.

Available architecture styles:
- n_tier: N-Tier (layered tiers separated by subnets)
- web_queue_worker: Web-Queue-Worker (front end + queue + background worker)
- microservices: Microservices (API gateway + autonomous services + per-service DB)
- event_driven: Event-Driven (producers → broker → consumers)
- big_data: Big Data (batch + real-time pipelines with orchestration)
- big_compute: Big Compute / HPC (job scheduler + parallel/coupled tasks)

Available design patterns (key highlights):
- cqrs, event_sourcing, saga, circuit_breaker, retry, cache_aside
- publisher_subscriber, competing_consumers, queue_based_load_leveling
- sidecar, ambassador, gateway_offloading, gateway_routing, gateway_aggregation
- strangler_fig, anti_corruption_layer, bulkhead, throttling, sharding
- deployment_stamps, geode, pipes_and_filters, valet_key, claim_check

Available reference architectures:
- baseline_foundry_chat: Baseline E2E Chat with Foundry
- azure_landing_zone: CAF Landing Zone with Hub-Spoke
- baseline_web_app: Baseline Zone-Redundant Web App
- ai_landing_zone: AI Workload in Azure Landing Zone
- microservices_aks: Microservices on AKS
"""


# GitHub Copilot / GitHub Models endpoint (OpenAI-compatible)
_GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com"


def _create_openai_client() -> AsyncOpenAI | AsyncAzureOpenAI:
    """Create the appropriate OpenAI client based on environment variables.

    Supports three providers:
      1. GitHub Copilot (GitHub Models) — set GITHUB_TOKEN
      2. Azure OpenAI — set AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY
      3. OpenAI — set OPENAI_API_KEY
    """
    # ── GitHub Copilot / GitHub Models ────────────────────────────
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        return AsyncOpenAI(
            base_url=_GITHUB_MODELS_ENDPOINT,
            api_key=github_token,
        )

    # ── Azure OpenAI ──────────────────────────────────────────────
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_key = os.environ.get("AZURE_OPENAI_API_KEY")

    if azure_endpoint and (azure_key or os.environ.get("AZURE_CLIENT_ID")):
        return AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_key,
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        )

    # ── OpenAI ────────────────────────────────────────────────────
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Set one of: GITHUB_TOKEN (GitHub Copilot), "
            "OPENAI_API_KEY, or AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY."
        )
    return AsyncOpenAI(api_key=api_key)


def _get_model() -> str:
    """Get the model name/deployment to use."""
    # Explicit model override always wins
    if os.environ.get("AZURE_OPENAI_DEPLOYMENT"):
        return os.environ["AZURE_OPENAI_DEPLOYMENT"]

    # GitHub Copilot defaults
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ.get("GITHUB_MODELS_MODEL", "gpt-4o")

    return os.environ.get("OPENAI_MODEL", "gpt-4o")


# Max conversation tokens to keep (approximate — 1 token ≈ 4 chars)
_MAX_CONVERSATION_CHARS = 40_000
_MAX_TOOL_RESULT_CHARS = 1_500


def _compact_tool_schemas(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reduce token usage by stripping verbose descriptions from tool schemas."""
    compact = []
    for tool in tools:
        fn = dict(tool["function"])
        # Keep only first sentence of description
        desc = fn.get("description", "")
        first_dot = desc.find(". ")
        if first_dot > 0:
            fn["description"] = desc[: first_dot + 1]

        # Simplify parameters: strip descriptions, keep only type info
        params = fn.get("parameters", {})
        if isinstance(params, dict) and "properties" in params:
            slim_props = {}
            for pname, pval in params["properties"].items():
                if isinstance(pval, dict):
                    slim = {"type": pval.get("type", "string")}
                    if "enum" in pval:
                        slim["enum"] = pval["enum"]
                    if "default" in pval:
                        slim["default"] = pval["default"]
                    slim_props[pname] = slim
                else:
                    slim_props[pname] = pval
            fn["parameters"] = {
                "type": params.get("type", "object"),
                "properties": slim_props,
                "required": params.get("required", []),
            }

        compact.append({"type": "function", "function": fn})
    return compact


def _truncate_conversation(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep system prompt + most recent messages within token budget.

    Tool-call assistant messages and their subsequent tool-response messages
    are treated as atomic groups so we never orphan a tool response without
    its preceding tool_calls assistant message.
    """
    if not messages:
        return messages

    # Always keep the system message
    system = [m for m in messages if m.get("role") == "system"]
    rest = [m for m in messages if m.get("role") != "system"]

    # Group messages into atomic chunks:
    #   - An assistant message with tool_calls + all following tool messages = one group
    #   - Everything else is its own group
    groups: list[list[dict[str, Any]]] = []
    i = 0
    while i < len(rest):
        msg = rest[i]
        role = msg.get("role", "")

        # Check if this is an assistant message with tool_calls
        has_tool_calls = (
            role == "assistant"
            and (msg.get("tool_calls") or (isinstance(msg.get("content"), type(None)) and i + 1 < len(rest) and rest[i + 1].get("role") == "tool"))
        )
        if has_tool_calls:
            group = [msg]
            i += 1
            # Collect all subsequent tool responses
            while i < len(rest) and rest[i].get("role") == "tool":
                group.append(rest[i])
                i += 1
            groups.append(group)
        else:
            groups.append([msg])
            i += 1

    # Walk backwards through groups, keeping recent ones within budget
    total_chars = sum(len(json.dumps(m)) for m in system)
    kept_groups: list[list[dict[str, Any]]] = []

    for group in reversed(groups):
        group_size = sum(len(json.dumps(m)) for m in group)
        if total_chars + group_size > _MAX_CONVERSATION_CHARS:
            break
        kept_groups.append(group)
        total_chars += group_size

    # Flatten kept groups back in original order
    kept_groups.reverse()
    result = list(system)
    for group in kept_groups:
        result.extend(group)
    return result


class AIAgent:
    """Orchestrates natural-language interaction with the Visio MCP server."""

    def __init__(self, mcp_client: VisioMCPClient) -> None:
        self._mcp = mcp_client
        self._client: AsyncOpenAI | AsyncAzureOpenAI | None = None
        self._model: str = ""
        self._provider_key: str = ""  # tracks which env config was used
        self._conversation: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

    @staticmethod
    def _current_provider_key() -> str:
        """Build a key from env vars so we detect config changes."""
        return "|".join([
            os.environ.get("GITHUB_TOKEN", "")[:8],
            os.environ.get("OPENAI_API_KEY", "")[:8],
            os.environ.get("AZURE_OPENAI_ENDPOINT", "")[:16],
            os.environ.get("GITHUB_MODELS_MODEL", ""),
            os.environ.get("OPENAI_MODEL", ""),
            os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""),
        ])

    def _ensure_client(self) -> None:
        key = self._current_provider_key()
        if self._client is None or self._provider_key != key:
            self._client = _create_openai_client()
            self._model = _get_model()
            self._provider_key = key

    async def chat(self, user_message: str) -> tuple[str, list[dict[str, Any]]]:
        """Process a user message and return (assistant_reply, tool_calls_log).

        The agent may make multiple rounds of tool calls before producing
        a final text response.
        """
        self._ensure_client()
        self._conversation.append({"role": "user", "content": user_message})

        tools = _compact_tool_schemas(self._mcp.get_tools_for_openai())
        tool_log: list[dict[str, Any]] = []
        max_rounds = 15  # safety cap

        for _ in range(max_rounds):
            # Truncate conversation to fit token limits
            messages = _truncate_conversation(self._conversation)

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
            )

            message = response.choices[0].message

            # If no tool calls, we have our final answer
            if not message.tool_calls:
                assistant_text = message.content or ""
                self._conversation.append({"role": "assistant", "content": assistant_text})
                return assistant_text, tool_log

            # Process each tool call
            self._conversation.append(message.model_dump())

            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args_raw = tool_call.function.arguments

                try:
                    fn_args = json.loads(fn_args_raw) if fn_args_raw else {}
                except json.JSONDecodeError:
                    fn_args = {}

                logger.info("Calling tool: %s(%s)", fn_name, fn_args)

                try:
                    result = self._mcp.call_tool(fn_name, fn_args)
                except Exception as e:
                    result = {"error": str(e)}

                tool_log.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "result": result,
                })

                self._conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)[:_MAX_TOOL_RESULT_CHARS],
                })

        # Exceeded max rounds
        return "I've completed the available operations. Let me know if you need anything else.", tool_log

    def reset_conversation(self) -> None:
        """Reset the conversation history (keeps system prompt)."""
        self._conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

    def inject_context(self, user_text: str, assistant_text: str) -> None:
        """Inject a synthetic user/assistant exchange so the model knows about
        sidebar actions (template apply, import, etc.) that bypassed the chat."""
        self._conversation.append({"role": "user", "content": user_text})
        self._conversation.append({"role": "assistant", "content": assistant_text})
