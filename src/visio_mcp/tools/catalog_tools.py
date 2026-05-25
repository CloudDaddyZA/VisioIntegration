"""Architecture catalog, styles, patterns, and resource tools."""

from __future__ import annotations

import json
import logging
from typing import Any

from visio_mcp._state import mcp, _diagram, _layout, _waf, _caf
from visio_mcp.azure_catalog import (
    AZURE_SHAPE_CATALOG,
    BOUNDARY_STYLES,
    CONNECTOR_STYLES,
)
from visio_mcp.reference_architectures import (
    AZURE_DIAGRAM_COLORS,
    REFERENCE_ARCHITECTURES,
    list_reference_architectures,
    list_architecture_styles,
    get_architecture_style,
    suggest_style_for_description,
    list_design_patterns,
    get_design_pattern,
    suggest_patterns_for_description,
    AZURE_ARCHITECTURE_CATALOG,
    list_architecture_catalog,
    search_architecture_catalog,
    get_architecture_catalog_entry,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# RESOURCES
# ═══════════════════════════════════════════════════════════════════

@mcp.resource("azure://shape-catalog")
def shape_catalog_resource() -> str:
    """Complete Azure shape catalog as a resource."""
    return json.dumps(
        {k: v.model_dump() for k, v in AZURE_SHAPE_CATALOG.items()},
        indent=2,
    )


@mcp.resource("azure://connector-styles")
def connector_styles_resource() -> str:
    """Available connector/line styles."""
    return json.dumps(CONNECTOR_STYLES, indent=2)


@mcp.resource("azure://boundary-styles")
def boundary_styles_resource() -> str:
    """Available boundary/container styles."""
    return json.dumps(BOUNDARY_STYLES, indent=2)


@mcp.resource("azure://reference-architectures")
def reference_architectures_resource() -> str:
    """Available Azure Architecture Center reference architecture templates."""
    return json.dumps(list_reference_architectures(), indent=2)


@mcp.resource("azure://diagram-standards")
def diagram_standards_resource() -> str:
    """Microsoft Azure Architecture Center diagram visual standards."""
    return json.dumps({
        "colors": AZURE_DIAGRAM_COLORS,
        "icon_guidelines": {
            "do": [
                "Use official Azure SVG icons at 1:1 aspect ratio",
                "Include product name label adjacent to every icon",
                "Use icons as they would appear within Azure",
            ],
            "dont": [
                "Don't crop, flip, or rotate icons",
                "Don't distort or change icon shape in any way",
                "Don't use Microsoft product icons to represent your product or service",
            ],
        },
        "layout_conventions": {
            "flow_direction": "Top-to-bottom (TB) or left-to-right (LR)",
            "workflow_steps": "Numbered circles on data-flow arrows",
            "boundaries": "Gray for RGs, light blue for VNet, light green for subnets, dashed borders for VNet/subnet",
            "connectors": "Solid for data flow, dashed for management/identity, dotted for private links",
        },
        "source": "https://learn.microsoft.com/en-us/azure/architecture/icons/",
    }, indent=2)


@mcp.resource("azure://architecture-styles")
def architecture_styles_resource() -> str:
    """Azure Architecture Center architecture styles — N-Tier, Microservices, Event-Driven, etc."""
    return json.dumps(list_architecture_styles(), indent=2)


# ═══════════════════════════════════════════════════════════════════
# TOOLS: Architecture Style Guidance
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def suggest_architecture_style(description: str) -> dict[str, Any]:
    """Suggest the best-fit Azure architecture style for a workload description.

    Analyzes the description against 14 architecture styles from
    the Azure Architecture Center including N-Tier, Web-Queue-Worker, Microservices,
    Event-Driven, Big Data, Big Compute (HPC), Dataflow, Big Data Analytics,
    Database Flow, AI/ML Pipeline, RAG AI App, Streaming Analytics, and more.

    Returns ranked suggestions with typical components, recommended Azure
    services, and diagram layout conventions for each style.

    Args:
        description: Natural language description of the workload or scenario
                     (e.g., "real-time IoT data processing pipeline").

    Returns:
        Ranked list of architecture styles with guidance on Azure services
        and diagram conventions.
    """
    suggestions = suggest_style_for_description(description)
    if not suggestions:
        return {
            "message": "No strong match found. Provide more detail about the workload.",
            "all_styles": [s["name"] for s in list_architecture_styles()],
        }
    return {
        "count": len(suggestions),
        "suggestions": suggestions,
    }


@mcp.tool()
def get_architecture_style_detail(style_key: str) -> dict[str, Any]:
    """Get detailed information about a specific architecture style.

    Returns full details including when to use it, typical components,
    recommended Azure services, and diagram layout conventions.

    Args:
        style_key: Architecture style key — e.g., n_tier, web_queue_worker,
                   microservices, event_driven, big_data, big_compute,
                   dataflow, big_data_analytics, database_flow, ai_ml_pipeline.

    Returns:
        Complete architecture style details or error if not found.
    """
    style = get_architecture_style(style_key)
    if not style:
        return {
            "error": f"Unknown style '{style_key}'",
            "available": [s["key"] for s in list_architecture_styles()],
        }
    return {
        "key": style.key,
        "name": style.name,
        "description": style.description,
        "source_url": style.source_url,
        "when_to_use": style.when_to_use,
        "typical_components": style.typical_components,
        "azure_services": style.azure_services,
        "flow_direction": style.flow_direction,
        "layout_strategy": style.layout_strategy,
        "diagram_conventions": style.diagram_conventions,
    }


# ═══════════════════════════════════════════════════════════════════
# RESOURCE: Cloud Design Patterns
# ═══════════════════════════════════════════════════════════════════

@mcp.resource("azure://design-patterns")
def design_patterns_resource() -> str:
    """Azure Architecture Center cloud design patterns — CQRS, Event Sourcing, Saga, etc."""
    return json.dumps(list_design_patterns(), indent=2)


# ═══════════════════════════════════════════════════════════════════
# TOOLS: Cloud Design Pattern Guidance
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def suggest_design_patterns(description: str) -> dict[str, Any]:
    """Suggest cloud design patterns for a workload challenge or scenario.

    Analyzes the description against 50 cloud design patterns from the
    Azure Architecture Center (e.g., CQRS, Event Sourcing, Saga, Circuit
    Breaker, Cache-Aside, Publisher-Subscriber, Strangler Fig, Data Lake,
    ETL/ELT, Lambda Architecture, MLOps CI/CD, RAG, etc.).

    Returns ranked suggestions with WAF pillar alignment, Azure services,
    related patterns, and diagram layout implications.

    Args:
        description: Natural language description of the challenge or scenario
                     (e.g., "handle distributed transactions across microservices",
                     "migrate a legacy monolith to Azure incrementally").

    Returns:
        Ranked list of design patterns with guidance.
    """
    suggestions = suggest_patterns_for_description(description)
    if not suggestions:
        return {
            "message": "No strong match found. Provide more detail about the challenge.",
            "all_patterns": [p["name"] for p in list_design_patterns()],
        }
    return {
        "count": len(suggestions),
        "suggestions": suggestions,
    }


@mcp.tool()
def get_design_pattern_detail(pattern_key: str) -> dict[str, Any]:
    """Get detailed information about a specific cloud design pattern.

    Returns full details including when to use it, when not to use it,
    WAF pillar alignment, Azure services, related patterns, and
    diagram layout implications.

    Args:
        pattern_key: Design pattern key — e.g., cqrs, event_sourcing, saga,
                     circuit_breaker, cache_aside, publisher_subscriber,
                     strangler_fig, sidecar, retry, bulkhead, etc.

    Returns:
        Complete design pattern details or error if not found.
    """
    pattern = get_design_pattern(pattern_key)
    if not pattern:
        return {
            "error": f"Unknown pattern '{pattern_key}'",
            "available": [p["key"] for p in list_design_patterns()],
        }
    return {
        "key": pattern.key,
        "name": pattern.name,
        "description": pattern.description,
        "source_url": pattern.source_url,
        "waf_pillars": pattern.waf_pillars,
        "when_to_use": pattern.when_to_use,
        "when_not_to_use": pattern.when_not_to_use,
        "related_patterns": pattern.related_patterns,
        "azure_services": pattern.azure_services,
        "diagram_implications": pattern.diagram_implications,
    }


# ═══════════════════════════════════════════════════════════════════
# TOOLS & RESOURCES: Azure Architecture Catalog (206 entries)
# ═══════════════════════════════════════════════════════════════════

@mcp.resource("azure://architecture-catalog")
def architecture_catalog_resource() -> str:
    """Full Azure Architecture Catalog — 206 reference architectures and solution ideas from Azure Architecture Center."""
    entries = []
    for entry in AZURE_ARCHITECTURE_CATALOG.values():
        entries.append({
            "key": entry.key,
            "name": entry.name,
            "type": entry.entry_type,
            "categories": entry.categories,
            "source_url": entry.source_url,
        })
    return json.dumps(entries, indent=2)


@mcp.tool()
def browse_architecture_catalog(
    category: str | None = None,
    entry_type: str | None = None,
) -> dict[str, Any]:
    """Browse the Azure Architecture Catalog (206 architectures & solutions).

    Filter by category (e.g. 'AI + Machine Learning', 'Networking', 'Security')
    and/or type ('Architecture', 'Reference Architecture', 'Solution Idea', 'Best Practice').

    Categories: AI + Machine Learning, Analytics, Compute, Containers, Databases,
    DevOps, Developer Tools, Hybrid + Multicloud, Identity, Integration,
    Internet of Things, Media, Migration, Networking, Security, Storage, Web.
    """
    results = list_architecture_catalog(
        category=category or "",
        entry_type=entry_type or "",
    )
    return {
        "count": len(results),
        "filters": {"category": category, "type": entry_type},
        "entries": results,
    }


@mcp.tool()
def search_arch_catalog(query: str) -> dict[str, Any]:
    """Search the Azure Architecture Catalog by keyword.

    Searches across names, summaries, categories, and Azure products.
    Returns up to 15 ranked results.
    """
    results = search_architecture_catalog(query)
    return {
        "query": query,
        "count": len(results),
        "results": results,
    }


@mcp.tool()
def get_arch_catalog_entry(key: str) -> dict[str, Any]:
    """Get full details for a specific Azure Architecture Catalog entry.

    Use browse_architecture_catalog or search_arch_catalog to find keys first.
    """
    entry = get_architecture_catalog_entry(key)
    if entry is None:
        return {"error": f"Architecture catalog entry '{key}' not found"}
    return entry


# ═══════════════════════════════════════════════════════════════════
