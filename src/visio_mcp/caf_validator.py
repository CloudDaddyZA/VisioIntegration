"""Azure Cloud Adoption Framework (CAF) validator for architecture diagrams.

Analyzes the diagram against CAF principles:
  1. Naming Convention  - Resource names follow Azure naming best practices
  2. Resource Organization - Proper hierarchy (management groups, subscriptions, resource groups)
  3. Network Topology   - Hub-spoke or other recommended patterns
  4. Identity and Access - AAD/Entra integration, managed identities
  5. Governance         - Policy, tagging, cost management
  6. Security Baseline  - Foundational security controls
  7. Management         - Monitoring, backup, disaster recovery

References: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/
"""

from __future__ import annotations

import re

from .models import CafPrinciple, DiagramState, ValidationFinding, ValidationReport


# CAF naming convention patterns (abbreviated prefixes)
# https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations
CAF_NAMING_PREFIXES: dict[str, str] = {
    "virtual_machine": "vm-",
    "vm_scale_set": "vmss-",
    "app_service": "app-",
    "app_service_plan": "plan-",
    "function_app": "func-",
    "container_instances": "ci-",
    "container_apps": "ca-",
    "kubernetes_service": "aks-",
    "container_registry": "cr",
    "virtual_network": "vnet-",
    "subnet": "snet-",
    "load_balancer": "lb-",
    "application_gateway": "agw-",
    "front_door": "afd-",
    "traffic_manager": "traf-",
    "dns_zone": "dnsz-",
    "private_endpoint": "pep-",
    "vpn_gateway": "vpng-",
    "expressroute": "erc-",
    "firewall": "afw-",
    "nsg": "nsg-",
    "bastion": "bas-",
    "nat_gateway": "ng-",
    "storage_account": "st",
    "sql_database": "sqldb-",
    "sql_managed_instance": "sqlmi-",
    "cosmos_db": "cosmos-",
    "mysql_database": "mysql-",
    "postgresql_database": "psql-",
    "redis_cache": "redis-",
    "key_vault": "kv-",
    "managed_identity": "id-",
    "api_management": "apim-",
    "logic_app": "logic-",
    "service_bus": "sb-",
    "event_hub": "evh-",
    "event_grid": "evg-",
    "log_analytics": "log-",
    "application_insights": "appi-",
    "data_factory": "adf-",
    "databricks": "dbw-",
    "openai_service": "oai-",
    "ai_search": "srch-",
    "iot_hub": "iot-",
    "resource_group": "rg-",
    "monitor": "mon-",
}


class CafValidator:
    """Validates an architecture diagram against Azure CAF principles."""

    def validate(self, state: DiagramState) -> ValidationReport:
        findings: list[ValidationFinding] = []
        findings.extend(self._check_naming(state))
        findings.extend(self._check_resource_organization(state))
        findings.extend(self._check_network_topology(state))
        findings.extend(self._check_identity(state))
        findings.extend(self._check_governance(state))
        findings.extend(self._check_security_baseline(state))
        findings.extend(self._check_management(state))

        score = self._calculate_score(findings)
        summary = self._generate_summary(findings, score)

        return ValidationReport(
            framework="CAF",
            score=score,
            findings=findings,
            summary=summary,
        )

    # ── Naming Convention ─────────────────────────────────────────

    def _check_naming(self, state: DiagramState) -> list[ValidationFinding]:
        findings = []

        for res in state.resources.values():
            expected_prefix = CAF_NAMING_PREFIXES.get(res.resource_type)
            if not expected_prefix:
                continue

            # Use caf_name property if set (e.g. by reference architectures),
            # otherwise fall back to the display name.
            caf_name = (res.properties or {}).get("caf_name", res.display_name)
            name_lower = caf_name.lower().replace(" ", "")

            # Check if name follows CAF naming convention
            if not name_lower.startswith(expected_prefix.lower()):
                findings.append(ValidationFinding(
                    severity="warning",
                    pillar=CafPrinciple.NAMING,
                    message=f"Resource '{res.display_name}' ({res.resource_type}) does not follow CAF naming convention.",
                    recommendation=f"CAF recommends prefix '{expected_prefix}' for {res.resource_type}. Example: '{expected_prefix}myapp-prod-eastus'.",
                    affected_resources=[res.id],
                ))

            # Check for environment and region in name
            env_pattern = r"(prod|dev|test|stag|qa|uat|sandbox)"
            if not re.search(env_pattern, name_lower, re.IGNORECASE):
                findings.append(ValidationFinding(
                    severity="info",
                    pillar=CafPrinciple.NAMING,
                    message=f"Resource '{res.display_name}' name does not include an environment indicator.",
                    recommendation="Include environment (prod, dev, test) in resource names for clarity. Example: 'vm-webapp-prod-eastus-001'.",
                    affected_resources=[res.id],
                ))

        # Check boundary naming
        for bnd in state.boundaries.values():
            if bnd.boundary_type == "resource_group":
                name_lower = bnd.display_name.lower().replace(" ", "")
                if not name_lower.startswith("rg-"):
                    findings.append(ValidationFinding(
                        severity="warning",
                        pillar=CafPrinciple.NAMING,
                        message=f"Resource group '{bnd.display_name}' does not follow CAF naming convention.",
                        recommendation="CAF recommends prefix 'rg-' for resource groups. Example: 'rg-myapp-prod-eastus'.",
                        affected_resources=[bnd.id],
                    ))

        return findings

    # ── Resource Organization ─────────────────────────────────────

    def _check_resource_organization(self, state: DiagramState) -> list[ValidationFinding]:
        findings = []
        boundary_types = {b.boundary_type for b in state.boundaries.values()}

        # Check: Resources not assigned to any resource group
        ungrouped = [
            r for r in state.resources.values() if r.group_id is None
        ]
        if ungrouped and state.boundaries:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=CafPrinciple.RESOURCE_ORGANIZATION,
                message=f"{len(ungrouped)} resource(s) not assigned to any boundary group.",
                recommendation="All Azure resources should belong to a resource group. Assign resources to appropriate boundary groups.",
                affected_resources=[r.id for r in ungrouped],
            ))

        # Check: No resource group boundaries
        rg_boundaries = [b for b in state.boundaries.values() if b.boundary_type == "resource_group"]
        if not rg_boundaries and len(state.resources) > 2:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=CafPrinciple.RESOURCE_ORGANIZATION,
                message="No resource group boundaries defined.",
                recommendation="Organize resources into resource groups based on lifecycle and ownership. Use separate RGs for shared infrastructure vs application-specific resources.",
                affected_resources=[],
            ))

        # Check: No subscription boundary
        if "subscription" not in boundary_types and len(state.resources) > 5:
            findings.append(ValidationFinding(
                severity="info",
                pillar=CafPrinciple.RESOURCE_ORGANIZATION,
                message="No subscription boundary shown in the architecture.",
                recommendation="Show subscription boundaries to clarify resource organization. CAF recommends subscription-level isolation for workloads.",
                affected_resources=[],
            ))

        # Check: Management group hierarchy (for large architectures)
        if len(state.resources) > 10 and "management_group" not in boundary_types:
            findings.append(ValidationFinding(
                severity="info",
                pillar=CafPrinciple.RESOURCE_ORGANIZATION,
                message="Large architecture without management group hierarchy.",
                recommendation="For enterprise architectures, show the management group hierarchy to demonstrate governance structure.",
                affected_resources=[],
            ))

        return findings

    # ── Network Topology ──────────────────────────────────────────

    def _check_network_topology(self, state: DiagramState) -> list[ValidationFinding]:
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}
        boundary_types = {b.boundary_type for b in state.boundaries.values()}

        vnet_boundaries = [b for b in state.boundaries.values() if b.boundary_type == "vnet"]
        has_vnets = bool(vnet_boundaries) or "virtual_network" in resource_types

        # Check: No VNet for IaaS resources
        iaas_types = {"virtual_machine", "vm_scale_set"}
        has_iaas = bool(resource_types & iaas_types)
        if has_iaas and not has_vnets:
            findings.append(ValidationFinding(
                severity="critical",
                pillar=CafPrinciple.NETWORK_TOPOLOGY,
                message="IaaS resources without Virtual Network boundaries.",
                recommendation="All IaaS resources must be deployed into VNets. Show VNet and subnet boundaries in the diagram.",
                affected_resources=[r.id for r in state.resources.values() if r.resource_type in iaas_types],
            ))

        # Check: Hub-spoke pattern for multi-VNet
        if len(vnet_boundaries) >= 2:
            has_hub_indicators = "firewall" in resource_types or "vpn_gateway" in resource_types or "expressroute" in resource_types
            if not has_hub_indicators:
                findings.append(ValidationFinding(
                    severity="warning",
                    pillar=CafPrinciple.NETWORK_TOPOLOGY,
                    message="Multiple VNets without clear hub-spoke topology.",
                    recommendation="CAF recommends hub-spoke network topology. The hub VNet should contain shared services (Firewall, VPN Gateway, Bastion).",
                    affected_resources=[],
                ))

        # Check: No subnet segmentation
        subnet_boundaries = [b for b in state.boundaries.values() if b.boundary_type == "subnet"]
        if has_vnets and not subnet_boundaries:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=CafPrinciple.NETWORK_TOPOLOGY,
                message="VNet without subnet segmentation.",
                recommendation="Segment VNets into subnets by workload tier (web, app, data, management). Apply NSGs per subnet.",
                affected_resources=[],
            ))

        # Check: No Bastion for remote access
        if has_iaas and "bastion" not in resource_types:
            findings.append(ValidationFinding(
                severity="info",
                pillar=CafPrinciple.NETWORK_TOPOLOGY,
                message="IaaS resources without Azure Bastion for secure remote access.",
                recommendation="Use Azure Bastion instead of public IP + RDP/SSH for secure VM access without exposing management ports.",
                affected_resources=[],
            ))

        return findings

    # ── Identity and Access ───────────────────────────────────────

    def _check_identity(self, state: DiagramState) -> list[ValidationFinding]:
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}

        # Check: No Entra ID
        if "entra_id" not in resource_types and len(state.resources) > 3:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=CafPrinciple.IDENTITY,
                message="No Microsoft Entra ID shown for centralized identity management.",
                recommendation="CAF requires centralized identity with Microsoft Entra ID. Show authentication flows and RBAC assignments.",
                affected_resources=[],
            ))

        # Check: No managed identity for service-to-service auth
        service_types = {"app_service", "function_app", "container_apps", "kubernetes_service", "logic_app", "data_factory"}
        services = [r for r in state.resources.values() if r.resource_type in service_types]
        if services and "managed_identity" not in resource_types:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=CafPrinciple.IDENTITY,
                message="Services present without managed identity for authentication.",
                recommendation="Use managed identities for all service-to-service authentication. Avoid storing credentials in code or configuration.",
                affected_resources=[r.id for r in services],
            ))

        return findings

    # ── Governance ────────────────────────────────────────────────

    def _check_governance(self, state: DiagramState) -> list[ValidationFinding]:
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}

        # Check: No Azure Policy
        if "policy" not in resource_types and len(state.resources) > 5:
            findings.append(ValidationFinding(
                severity="info",
                pillar=CafPrinciple.GOVERNANCE,
                message="No Azure Policy shown for governance.",
                recommendation="Use Azure Policy to enforce tagging, allowed regions, allowed SKUs, and compliance requirements.",
                affected_resources=[],
            ))

        # Check: Resources without tags/properties
        untagged = [
            r for r in state.resources.values()
            if not r.properties.get("tags") and r.resource_type not in {"user", "internet", "on_premises"}
        ]
        if len(untagged) > 3:
            findings.append(ValidationFinding(
                severity="info",
                pillar=CafPrinciple.GOVERNANCE,
                message="Resources without tag properties defined.",
                recommendation="Define a tagging strategy. CAF recommends tags for: Environment, Owner, CostCenter, Application, Criticality.",
                affected_resources=[r.id for r in untagged[:5]],
            ))

        return findings

    # ── Security Baseline ─────────────────────────────────────────

    def _check_security_baseline(self, state: DiagramState) -> list[ValidationFinding]:
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}

        # Check: No Defender for Cloud
        if "defender_for_cloud" not in resource_types and len(state.resources) > 3:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=CafPrinciple.SECURITY_BASELINE,
                message="Microsoft Defender for Cloud not included in the architecture.",
                recommendation="CAF Security Baseline requires Defender for Cloud for continuous security posture management.",
                affected_resources=[],
            ))

        # Check: No Sentinel for SIEM
        if "sentinel" not in resource_types and len(state.resources) > 8:
            findings.append(ValidationFinding(
                severity="info",
                pillar=CafPrinciple.SECURITY_BASELINE,
                message="Microsoft Sentinel not shown for security information and event management.",
                recommendation="Consider Microsoft Sentinel for cloud-native SIEM and SOAR capabilities.",
                affected_resources=[],
            ))

        return findings

    # ── Management and Monitoring ─────────────────────────────────

    def _check_management(self, state: DiagramState) -> list[ValidationFinding]:
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}

        monitoring_types = {"monitor", "log_analytics", "application_insights"}
        has_monitoring = bool(resource_types & monitoring_types)

        if not has_monitoring and len(state.resources) > 2:
            findings.append(ValidationFinding(
                severity="critical",
                pillar=CafPrinciple.MANAGEMENT,
                message="No monitoring or management components in the architecture.",
                recommendation="CAF Management requires Azure Monitor and Log Analytics for centralized monitoring, alerting, and diagnostics.",
                affected_resources=[],
            ))

        # Check: Log Analytics workspace
        if "log_analytics" not in resource_types and len(state.resources) > 3:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=CafPrinciple.MANAGEMENT,
                message="No Log Analytics workspace for centralized log collection.",
                recommendation="Deploy a central Log Analytics workspace. All resources should send diagnostic logs to this workspace.",
                affected_resources=[],
            ))

        return findings

    # ── Scoring ───────────────────────────────────────────────────

    def _calculate_score(self, findings: list[ValidationFinding]) -> float:
        if not findings:
            return 100.0

        deductions = 0.0
        for f in findings:
            if f.severity == "critical":
                deductions += 15
            elif f.severity == "warning":
                deductions += 8
            elif f.severity == "info":
                deductions += 2

        return max(0.0, min(100.0, 100.0 - deductions))

    def _generate_summary(self, findings: list[ValidationFinding], score: float) -> str:
        critical = sum(1 for f in findings if f.severity == "critical")
        warnings = sum(1 for f in findings if f.severity == "warning")
        info = sum(1 for f in findings if f.severity == "info")

        principles_affected = set(f.pillar for f in findings if f.severity in ("critical", "warning"))

        parts = [f"CAF Score: {score:.0f}/100."]
        if critical:
            parts.append(f"{critical} critical issue(s).")
        if warnings:
            parts.append(f"{warnings} warning(s).")
        if info:
            parts.append(f"{info} informational note(s).")
        if principles_affected:
            principle_names = ", ".join(
                p.value if isinstance(p, CafPrinciple) else str(p) for p in sorted(principles_affected, key=str)
            )
            parts.append(f"Principles needing attention: {principle_names}.")

        return " ".join(parts)
