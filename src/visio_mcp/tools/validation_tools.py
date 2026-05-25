"""WAF/CAF validation tools and architecture improvement suggestions."""

from __future__ import annotations

import json
import logging
from typing import Any

from visio_mcp._state import mcp, _diagram, _layout, _waf, _caf
from visio_mcp.azure_catalog import AZURE_SHAPE_CATALOG
from visio_mcp.caf_validator import CAF_NAMING_PREFIXES
from visio_mcp.models import WafPillar

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# TOOL: validate_waf
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def validate_waf(pillar: str | None = None) -> dict[str, Any]:
    """Validate the current architecture against the Azure Well-Architected Framework.

    Checks the diagram against all five WAF pillars:
      - Reliability: HA, failover, multi-region, availability zones
      - Security: Key Vault, NSGs, private endpoints, WAF, identity
      - Cost Optimization: autoscaling, right-sizing, tier selection
      - Operational Excellence: monitoring, CI/CD, governance
      - Performance Efficiency: caching, CDN, async patterns

    Args:
        pillar: Optional - filter to a specific pillar
                ('Reliability', 'Security', 'Cost Optimization',
                 'Operational Excellence', 'Performance Efficiency').
                Pass None to check all pillars.

    Returns:
        Validation report with score, findings, and recommendations.
    """
    report = _waf.validate(_diagram.state)

    if pillar:
        # Filter findings to a specific pillar
        try:
            target_pillar = WafPillar(pillar)
        except ValueError:
            return {
                "status": "error",
                "message": f"Unknown pillar '{pillar}'.",
                "valid_pillars": [p.value for p in WafPillar],
            }
        report.findings = [
            f for f in report.findings if f.pillar == target_pillar or f.pillar == target_pillar.value
        ]

    return {
        "framework": "WAF",
        "score": report.score,
        "summary": report.summary,
        "finding_count": len(report.findings),
        "findings": [
            {
                "severity": f.severity,
                "pillar": f.pillar.value if hasattr(f.pillar, "value") else f.pillar,
                "message": f.message,
                "recommendation": f.recommendation,
                "affected_resources": f.affected_resources,
                "page": f.page,
                "page_name": f.page_name or "",
            }
            for f in report.findings
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: validate_caf
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def validate_caf(principle: str | None = None) -> dict[str, Any]:
    """Validate the current architecture against the Azure Cloud Adoption Framework.

    Checks the diagram against CAF principles:
      - Naming Convention: resource names follow CAF abbreviation guidance
      - Resource Organization: management groups, subscriptions, resource groups
      - Network Topology: hub-spoke, subnet segmentation
      - Identity and Access: Entra ID, managed identities
      - Governance: Azure Policy, tagging strategy
      - Security Baseline: Defender for Cloud, Sentinel
      - Management: monitoring, Log Analytics

    Args:
        principle: Optional - filter to a specific principle. Pass None to check all.

    Returns:
        Validation report with score, findings, and recommendations.
    """
    report = _caf.validate(_diagram.state)

    if principle:
        report.findings = [f for f in report.findings if principle.lower() in str(f.pillar).lower()]

    return {
        "framework": "CAF",
        "score": report.score,
        "summary": report.summary,
        "finding_count": len(report.findings),
        "findings": [
            {
                "severity": f.severity,
                "principle": f.pillar.value if hasattr(f.pillar, "value") else f.pillar,
                "message": f.message,
                "recommendation": f.recommendation,
                "affected_resources": f.affected_resources,
                "page": f.page,
                "page_name": f.page_name or "",
            }
            for f in report.findings
        ],
    }



# ═══════════════════════════════════════════════════════════════════
# TOOL: get_waf_tips
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_waf_tips(resource_type: str) -> dict[str, Any]:
    """Get WAF (Well-Architected Framework) tips for a specific Azure resource type.

    Args:
        resource_type: The resource type key (e.g., 'virtual_machine', 'sql_database').

    Returns:
        WAF considerations organized by pillar for the specified resource.
    """
    shape_info = AZURE_SHAPE_CATALOG.get(resource_type)
    if not shape_info:
        return {
            "status": "error",
            "message": f"Unknown resource type '{resource_type}'.",
        }

    return {
        "resource_type": resource_type,
        "display_name": shape_info.display_name,
        "waf_considerations": shape_info.waf_considerations or {"note": "No specific WAF tips cataloged for this resource."},
    }


# ═══════════════════════════════════════════════════════════════════
# TOOL: suggest_architecture
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def suggest_architecture_improvements() -> dict[str, Any]:
    """Analyze the current diagram and suggest architectural improvements.

    Runs both WAF and CAF validations and provides a prioritized list of
    improvements with specific resources to add.

    Returns:
        Combined analysis with prioritized recommendations.
    """
    waf_report = _waf.validate(_diagram.state)
    caf_report = _caf.validate(_diagram.state)

    # Collect resources to suggest adding
    resource_types = {r.resource_type for r in _diagram.state.resources.values()}
    suggestions = []

    # Security essentials
    if "key_vault" not in resource_types:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "key_vault",
            "reason": "WAF Security + CAF Security Baseline: centralized secrets management",
            "priority": "high",
        })
    if "managed_identity" not in resource_types:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "managed_identity",
            "reason": "WAF Security + CAF Identity: passwordless service-to-service auth",
            "priority": "high",
        })

    # Monitoring essentials
    monitoring_types = {"monitor", "log_analytics", "application_insights"}
    if not (resource_types & monitoring_types):
        suggestions.append({
            "action": "add_resource",
            "resource_type": "log_analytics",
            "reason": "WAF Operational Excellence + CAF Management: centralized logging",
            "priority": "high",
        })
        suggestions.append({
            "action": "add_resource",
            "resource_type": "application_insights",
            "reason": "WAF Operational Excellence: application performance monitoring",
            "priority": "medium",
        })

    # Network security
    has_vnet = any(b.boundary_type in ("vnet", "subnet") for b in _diagram.state.boundaries.values())
    if has_vnet and "firewall" not in resource_types and "nsg" not in resource_types:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "firewall",
            "reason": "WAF Security + CAF Network Topology: centralized network security",
            "priority": "high",
        })

    # Identity
    if "entra_id" not in resource_types:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "entra_id",
            "reason": "CAF Identity: centralized identity management",
            "priority": "medium",
        })

    # Governance
    if "policy" not in resource_types and len(_diagram.state.resources) > 5:
        suggestions.append({
            "action": "add_resource",
            "resource_type": "policy",
            "reason": "CAF Governance: enforce compliance and standards",
            "priority": "low",
        })

    # Boundary suggestions
    rg_boundaries = [b for b in _diagram.state.boundaries.values() if b.boundary_type == "resource_group"]
    if not rg_boundaries and len(_diagram.state.resources) > 2:
        suggestions.append({
            "action": "add_boundary",
            "boundary_type": "resource_group",
            "reason": "CAF Resource Organization: group resources by lifecycle",
            "priority": "medium",
        })

    return {
        "waf_score": waf_report.score,
        "caf_score": caf_report.score,
        "waf_summary": waf_report.summary,
        "caf_summary": caf_report.summary,
        "critical_issues": [
            {
                "source": f.pillar.value if hasattr(f.pillar, "value") else str(f.pillar),
                "message": f.message,
                "recommendation": f.recommendation,
            }
            for f in waf_report.findings + caf_report.findings
            if f.severity == "critical"
        ],
        "suggested_additions": suggestions,
    }


