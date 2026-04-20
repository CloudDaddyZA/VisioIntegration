"""Azure Well-Architected Framework (WAF) validator for architecture diagrams.

Analyzes the diagram state against the five WAF pillars:
  1. Reliability
  2. Security
  3. Cost Optimization
  4. Operational Excellence
  5. Performance Efficiency

Includes reference architecture alignment checks per Azure Architecture Center.
References: https://learn.microsoft.com/en-us/azure/well-architected/
"""

from __future__ import annotations

from .azure_catalog import AZURE_SHAPE_CATALOG
from .models import DiagramState, ValidationFinding, ValidationReport, WafPillar


class WafValidator:
    """Validates an architecture diagram against the Azure WAF pillars."""

    def validate(self, state: DiagramState) -> ValidationReport:
        """Run all WAF pillar checks and return a scored validation report.

        Evaluates the diagram against the 5 WAF pillars plus reference
        architecture alignment. Each check appends findings with severity
        levels (critical/warning/info) that are deducted from a base score of 100.

        Args:
            state: The current diagram state to validate.

        Returns:
            A ValidationReport with score (0-100), findings list, and summary.
        """
        findings: list[ValidationFinding] = []
        findings.extend(self._check_reliability(state))
        findings.extend(self._check_security(state))
        findings.extend(self._check_cost_optimization(state))
        findings.extend(self._check_operational_excellence(state))
        findings.extend(self._check_performance_efficiency(state))
        findings.extend(self._check_reference_arch_alignment(state))

        # Annotate findings with page info from affected resources
        self._annotate_pages(findings, state)

        score = self._calculate_score(findings)
        summary = self._generate_summary(findings, score)

        return ValidationReport(
            framework="WAF",
            score=score,
            findings=findings,
            summary=summary,
        )

    # ── Reliability ───────────────────────────────────────────────

    def _check_reliability(self, state: DiagramState) -> list[ValidationFinding]:
        """Check Reliability pillar: load balancing, multi-region, AZ, DB failover, storage redundancy."""
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}
        resources = list(state.resources.values())

        # Check: No load balancer or gateway for multiple compute instances
        compute_types = {"virtual_machine", "vm_scale_set", "app_service", "container_apps", "kubernetes_service"}
        compute_resources = [r for r in resources if r.resource_type in compute_types]
        lb_types = {"load_balancer", "application_gateway", "front_door", "traffic_manager"}
        has_lb = bool(resource_types & lb_types)

        if len(compute_resources) >= 2 and not has_lb:
            findings.append(ValidationFinding(
                severity="critical",
                pillar=WafPillar.RELIABILITY,
                message="Multiple compute resources without a load balancer or gateway.",
                recommendation="Add a Load Balancer, Application Gateway, or Front Door to distribute traffic and enable failover.",
                affected_resources=[r.id for r in compute_resources],
            ))

        # Check: Single region deployment
        # Detect multi-region via: resource properties, region boundaries, global load-balancer
        # presence (Traffic Manager / Front Door), or region names in resource/boundary names.
        regions = set()
        for r in resources:
            region = r.properties.get("region") or r.properties.get("location")
            if region:
                regions.add(region.lower())
        region_boundaries = [b for b in state.boundaries.values() if b.boundary_type == "region"]
        # Also infer regions from boundary display names that contain common Azure region patterns
        _REGION_KEYWORDS = {
            "eastus", "eastus2", "westus", "westus2", "westus3", "centralus", "northcentralus",
            "southcentralus", "westcentralus", "canadacentral", "canadaeast",
            "westeurope", "northeurope", "uksouth", "ukwest", "francecentral",
            "germanywestcentral", "norwayeast", "switzerlandnorth", "swedencentral",
            "eastasia", "southeastasia", "japaneast", "japanwest", "koreacentral",
            "australiaeast", "australiasoutheast", "centralindia", "southindia",
            "brazilsouth", "southafricanorth", "uaenorth", "qatarcentral",
        }
        for b in state.boundaries.values():
            name_lower = b.display_name.lower().replace(" ", "").replace("-", "").replace("_", "")
            for kw in _REGION_KEYWORDS:
                if kw in name_lower:
                    regions.add(kw)
                    break
        # Infer regions from resource display names
        for r in resources:
            name_lower = r.display_name.lower().replace(" ", "").replace("-", "").replace("_", "")
            for kw in _REGION_KEYWORDS:
                if kw in name_lower:
                    regions.add(kw)
                    break
        # Global failover resources count as multi-region intent
        global_lb_types = {"traffic_manager", "front_door"}
        has_global_lb = bool(resource_types & global_lb_types)

        is_multi_region = len(regions) > 1 or len(region_boundaries) > 1 or has_global_lb
        if not is_multi_region:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=WafPillar.RELIABILITY,
                message="Architecture appears to be single-region. No multi-region redundancy detected.",
                recommendation="Consider deploying critical workloads across multiple Azure regions with Traffic Manager or Front Door for global failover.",
                affected_resources=[],
            ))

        # Check: No availability zones
        az_boundaries = [b for b in state.boundaries.values() if b.boundary_type == "availability_zone"]
        # Also detect AZ references in boundary/resource names
        _az_keywords = {"availability zone", "availability_zone", "az-1", "az-2", "az-3", "az 1", "az 2", "az 3", "zone 1", "zone 2", "zone 3"}
        az_in_names = any(
            any(kw in b.display_name.lower() for kw in _az_keywords)
            for b in state.boundaries.values()
        ) or any(
            any(kw in r.display_name.lower() for kw in _az_keywords)
            for r in resources
        )
        if compute_resources and not az_boundaries and not az_in_names:
            az_mentioned = any(
                r.properties.get("availability_zone") or r.properties.get("zones")
                for r in resources
            )
            if not az_mentioned:
                findings.append(ValidationFinding(
                    severity="warning",
                    pillar=WafPillar.RELIABILITY,
                    message="No Availability Zones detected in the architecture.",
                    recommendation="Deploy critical resources across Availability Zones for zone-level redundancy.",
                    affected_resources=[r.id for r in compute_resources],
                ))

        # Check: Database without replication/failover
        # Detect via: explicit properties, connections between same-type DBs (geo-replication),
        # boundary notes mentioning failover/replication, or multiple DBs of same type in different regions.
        db_types = {"sql_database", "sql_managed_instance", "cosmos_db", "mysql_database", "postgresql_database"}
        db_resources = [r for r in resources if r.resource_type in db_types]

        # Check if there are DB-to-DB connections (indicating replication)
        db_ids = {r.id for r in db_resources}
        has_db_replication_conn = any(
            c.source_id in db_ids and c.target_id in db_ids
            for c in state.connections.values()
        )
        # Check for boundary notes mentioning replication/failover
        _replication_keywords = {"geo-replication", "replication", "failover", "auto-failover", "geo_replication", "failover_group"}
        has_replication_boundary = any(
            any(kw in b.display_name.lower() for kw in _replication_keywords)
            for b in state.boundaries.values()
        )
        # Check if multiple DBs of same type exist (implies replication across regions)
        from collections import Counter
        db_type_counts = Counter(r.resource_type for r in db_resources)
        has_paired_dbs = any(count >= 2 for count in db_type_counts.values())

        # Only flag individual DBs if none of the above global indicators are present
        global_db_failover = has_db_replication_conn or has_replication_boundary or has_paired_dbs
        for db in db_resources:
            has_geo = db.properties.get("geo_replication") or db.properties.get("failover_group")
            if not has_geo and not global_db_failover:
                findings.append(ValidationFinding(
                    severity="warning",
                    pillar=WafPillar.RELIABILITY,
                    message=f"Database '{db.display_name}' has no geo-replication or failover group configured.",
                    recommendation="Enable geo-replication or auto-failover groups for business-critical databases.",
                    affected_resources=[db.id],
                ))

        # Check: Storage without redundancy
        storage_resources = [r for r in resources if r.resource_type in {"storage_account", "blob_storage", "data_lake_storage"}]
        for sr in storage_resources:
            replication = sr.properties.get("replication") or sr.properties.get("sku")
            if replication and "LRS" in str(replication).upper():
                findings.append(ValidationFinding(
                    severity="warning",
                    pillar=WafPillar.RELIABILITY,
                    message=f"Storage '{sr.display_name}' uses LRS with no geo-redundancy.",
                    recommendation="Use GRS or RA-GRS for production data that requires durability across regions.",
                    affected_resources=[sr.id],
                ))

        return findings

    # ── Security ──────────────────────────────────────────────────

    def _check_security(self, state: DiagramState) -> list[ValidationFinding]:
        """Check Security pillar: Key Vault, managed identity, NSG/Firewall, private endpoints, DDoS, WAF."""
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}
        resources = list(state.resources.values())
        connection_types = {c.connection_type for c in state.connections.values()}

        # Check: No Key Vault
        if "key_vault" not in resource_types and len(resources) > 2:
            findings.append(ValidationFinding(
                severity="critical",
                pillar=WafPillar.SECURITY,
                message="No Azure Key Vault in the architecture for secrets/certificate management.",
                recommendation="Add Key Vault to manage secrets, keys, and certificates. Use managed identity for access.",
                affected_resources=[],
            ))

        # Check: No managed identity
        if "managed_identity" not in resource_types and len(resources) > 2:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=WafPillar.SECURITY,
                message="No Managed Identity shown in the architecture.",
                recommendation="Use system-assigned or user-assigned managed identities instead of connection strings or keys for service-to-service authentication.",
                affected_resources=[],
            ))

        # Check: No NSG or Firewall for VNet-deployed resources
        has_vnet = any(
            b.boundary_type in {"vnet", "subnet"} for b in state.boundaries.values()
        ) or "virtual_network" in resource_types
        has_nsg = "nsg" in resource_types or any(
            b.boundary_type == "nsg" for b in state.boundaries.values()
        )
        has_firewall = "firewall" in resource_types

        if has_vnet and not has_nsg and not has_firewall:
            findings.append(ValidationFinding(
                severity="critical",
                pillar=WafPillar.SECURITY,
                message="Virtual network present without NSG or Azure Firewall.",
                recommendation="Apply NSGs to all subnets. Consider Azure Firewall for centralized network security.",
                affected_resources=[],
            ))

        # Check: No private endpoints for data services
        data_types = {"sql_database", "cosmos_db", "storage_account", "key_vault", "redis_cache"}
        data_resources = [r for r in resources if r.resource_type in data_types]
        has_private_endpoint = "private_endpoint" in resource_types or "private_link" in resource_types
        if data_resources and not has_private_endpoint:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=WafPillar.SECURITY,
                message="Data services present without Private Endpoints.",
                recommendation="Use Private Endpoints for all PaaS data services to keep traffic on the Microsoft backbone network.",
                affected_resources=[r.id for r in data_resources],
            ))

        # Check: No DDoS protection for public-facing architecture
        public_types = {"front_door", "application_gateway", "load_balancer", "api_management"}
        has_public = bool(resource_types & public_types)
        if has_public and "ddos_protection" not in resource_types:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=WafPillar.SECURITY,
                message="Public-facing resources without DDoS Protection Standard.",
                recommendation="Enable Azure DDoS Protection Standard on VNets with public-facing resources.",
                affected_resources=[],
            ))

        # Check: No WAF for web applications
        web_types = {"app_service", "static_web_app", "container_apps"}
        web_resources = [r for r in resources if r.resource_type in web_types]
        has_waf = "application_gateway" in resource_types or "front_door" in resource_types
        if web_resources and not has_waf:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=WafPillar.SECURITY,
                message="Web applications without Web Application Firewall (WAF).",
                recommendation="Place web applications behind Application Gateway with WAF v2 or Front Door with WAF policy.",
                affected_resources=[r.id for r in web_resources],
            ))

        # Check: No identity provider
        if "entra_id" not in resource_types and "app_registration" not in resource_types and len(resources) > 3:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.SECURITY,
                message="No Microsoft Entra ID shown for identity management.",
                recommendation="Consider including Entra ID in the architecture to show authentication and authorization flows.",
                affected_resources=[],
            ))

        # Check: No Defender for Cloud
        if "defender_for_cloud" not in resource_types and len(resources) > 5:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.SECURITY,
                message="Microsoft Defender for Cloud not shown in the architecture.",
                recommendation="Enable Defender for Cloud for continuous security assessment and threat protection.",
                affected_resources=[],
            ))

        return findings

    # ── Cost Optimization ─────────────────────────────────────────

    def _check_cost_optimization(self, state: DiagramState) -> list[ValidationFinding]:
        """Check Cost Optimization pillar: autoscaling, premium SKU justification, standalone VMs."""
        findings = []
        resources = list(state.resources.values())

        # Check: Dedicated compute without autoscaling indication
        scalable_types = {"vm_scale_set", "app_service", "container_apps", "kubernetes_service"}
        for r in resources:
            if r.resource_type in scalable_types:
                has_autoscale = r.properties.get("autoscale") or r.properties.get("scaling")
                if not has_autoscale:
                    findings.append(ValidationFinding(
                        severity="info",
                        pillar=WafPillar.COST_OPTIMIZATION,
                        message=f"'{r.display_name}' does not indicate autoscaling configuration.",
                        recommendation="Configure autoscale rules to scale down during low-demand periods and reduce costs.",
                        affected_resources=[r.id],
                    ))

        # Check: Premium SKUs without justification
        for r in resources:
            sku = str(r.properties.get("sku", "")).lower()
            tier = str(r.properties.get("tier", "")).lower()
            if "premium" in sku or "premium" in tier:
                findings.append(ValidationFinding(
                    severity="info",
                    pillar=WafPillar.COST_OPTIMIZATION,
                    message=f"'{r.display_name}' uses Premium tier. Ensure it's justified by requirements.",
                    recommendation="Evaluate if Standard tier meets your SLA needs. Reserve capacity for predictable workloads.",
                    affected_resources=[r.id],
                ))

        # Check: Standalone VMs (not in VMSS or managed by AKS)
        standalone_vms = [r for r in resources if r.resource_type == "virtual_machine"]
        if len(standalone_vms) > 3:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=WafPillar.COST_OPTIMIZATION,
                message=f"{len(standalone_vms)} standalone VMs detected. Consider using VMSS or PaaS.",
                recommendation="Migrate to VM Scale Sets for elasticity, or consider PaaS alternatives (App Service, Container Apps) to reduce management overhead and improve cost efficiency.",
                affected_resources=[r.id for r in standalone_vms],
            ))

        return findings

    # ── Operational Excellence ────────────────────────────────────

    def _check_operational_excellence(self, state: DiagramState) -> list[ValidationFinding]:
        """Check Operational Excellence pillar: monitoring, CI/CD, Azure Policy."""
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}

        # Check: No monitoring
        monitoring_types = {"monitor", "log_analytics", "application_insights"}
        has_monitoring = bool(resource_types & monitoring_types)
        if not has_monitoring and len(state.resources) > 2:
            findings.append(ValidationFinding(
                severity="critical",
                pillar=WafPillar.OPERATIONAL_EXCELLENCE,
                message="No monitoring or observability components in the architecture.",
                recommendation="Add Azure Monitor, Log Analytics, and Application Insights for observability. This is essential for production operations.",
                affected_resources=[],
            ))

        # Check: No DevOps / CI/CD
        cicd_types = {"devops", "github_actions", "data_factory", "logic_app"}
        has_cicd = bool(resource_types & cicd_types)
        # Also detect CI/CD from resource names
        _cicd_keywords = {"ci/cd", "cicd", "pipeline", "devops", "github actions", "deployment"}
        if not has_cicd:
            has_cicd = any(
                any(kw in r.display_name.lower() for kw in _cicd_keywords)
                for r in state.resources.values()
            )
        if not has_cicd and len(state.resources) > 3:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.OPERATIONAL_EXCELLENCE,
                message="No CI/CD or DevOps pipeline shown in the architecture.",
                recommendation="Consider including Azure DevOps or GitHub Actions in the architecture to show deployment automation.",
                affected_resources=[],
            ))

        # Check: No Azure Policy for governance
        if "policy" not in resource_types and len(state.resources) > 5:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.OPERATIONAL_EXCELLENCE,
                message="No Azure Policy shown for governance and compliance.",
                recommendation="Use Azure Policy to enforce organizational standards and assess compliance at scale.",
                affected_resources=[],
            ))

        return findings

    # ── Performance Efficiency ────────────────────────────────────

    def _check_performance_efficiency(self, state: DiagramState) -> list[ValidationFinding]:
        """Check Performance Efficiency pillar: caching, CDN, async messaging."""
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}
        resources = list(state.resources.values())

        # Check: No caching layer
        has_cache = "redis_cache" in resource_types or "cdn_profile" in resource_types
        has_web = bool(resource_types & {"app_service", "container_apps", "kubernetes_service", "static_web_app"})
        has_db = bool(resource_types & {"sql_database", "cosmos_db", "mysql_database", "postgresql_database"})

        if has_web and has_db and not has_cache:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.PERFORMANCE_EFFICIENCY,
                message="Web application with database but no caching layer.",
                recommendation="Consider adding Azure Cache for Redis for session/data caching, or Azure CDN for static content caching.",
                affected_resources=[],
            ))

        # Check: No CDN for static content
        static_types = {"static_web_app", "blob_storage", "storage_account"}
        has_static = bool(resource_types & static_types)
        if has_static and "cdn_profile" not in resource_types and "front_door" not in resource_types:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.PERFORMANCE_EFFICIENCY,
                message="Static content without CDN or Front Door for global distribution.",
                recommendation="Use Azure CDN or Front Door to cache and deliver static content closer to users.",
                affected_resources=[],
            ))

        # Check: Synchronous data pipeline
        has_analytics = bool(resource_types & {"synapse_analytics", "databricks", "data_factory", "stream_analytics"})
        has_messaging = bool(resource_types & {"service_bus", "event_hub", "event_grid"})
        if has_analytics and not has_messaging:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.PERFORMANCE_EFFICIENCY,
                message="Analytics pipeline without asynchronous messaging.",
                recommendation="Use Event Hubs or Service Bus for decoupled, asynchronous data ingestion to improve throughput.",
                affected_resources=[],
            ))

        return findings

    # ── Reference Architecture Alignment ──────────────────────────

    def _check_reference_arch_alignment(self, state: DiagramState) -> list[ValidationFinding]:
        """Check alignment with Azure Architecture Center diagram standards."""
        findings = []
        resource_types = {r.resource_type for r in state.resources.values()}

        # Check: Private endpoints for PaaS services (per baseline architecture pattern)
        paas_types = {
            "sql_database", "cosmos_db", "storage_account", "key_vault",
            "openai_service", "ai_search", "cognitive_services",
            "redis_cache", "service_bus", "event_hub", "container_registry",
        }
        paas_in_diagram = resource_types & paas_types
        has_private_endpoints = "private_endpoint" in resource_types
        if paas_in_diagram and not has_private_endpoints:
            findings.append(ValidationFinding(
                severity="warning",
                pillar=WafPillar.SECURITY,
                message="PaaS services without explicit private endpoints (per Azure Architecture Center baseline pattern).",
                recommendation=(
                    "Azure reference architectures show private endpoints as explicit shapes in a dedicated subnet. "
                    "Add private_endpoint resources connected to each PaaS service for network isolation."
                ),
                affected_resources=list(paas_in_diagram),
            ))

        # Check: Dedicated subnets per service type (per MS diagram conventions)
        subnet_boundaries = [b for b in state.boundaries.values() if b.boundary_type == "subnet"]
        vnet_boundaries = [b for b in state.boundaries.values() if b.boundary_type == "vnet"]
        if vnet_boundaries and len(subnet_boundaries) < 2:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.SECURITY,
                message="VNet has fewer than 2 subnets. Azure reference architectures use dedicated subnets per function.",
                recommendation=(
                    "Separate subnets for: App Gateway, App Service integration, private endpoints, "
                    "and optionally Bastion, Firewall. See Azure Architecture Center baseline patterns."
                ),
                affected_resources=[b.id for b in vnet_boundaries],
            ))

        # Check: WAF on ingress (all baseline architectures require this)
        has_agw = "application_gateway" in resource_types
        has_front_door = "front_door" in resource_types
        internet_facing = any(
            r.resource_type in ("app_service", "container_apps", "kubernetes_service", "static_web_app")
            for r in state.resources.values()
        )
        if internet_facing and not (has_agw or has_front_door):
            findings.append(ValidationFinding(
                severity="warning",
                pillar=WafPillar.SECURITY,
                message="Internet-facing compute without WAF protection (Application Gateway WAF or Front Door).",
                recommendation=(
                    "Per Azure Architecture Center baselines, all internet-facing apps should be behind "
                    "Application Gateway with WAF v2 or Azure Front Door with WAF. "
                    "See: baseline-zone-redundant web app architecture."
                ),
                affected_resources=[],
            ))

        # Check: Egress control through Firewall (baseline pattern)
        has_firewall = "firewall" in resource_types
        has_compute = bool(resource_types & {"container_apps", "kubernetes_service", "app_service", "virtual_machine"})
        if has_compute and not has_firewall:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.SECURITY,
                message="No Azure Firewall for egress control.",
                recommendation=(
                    "Azure baseline architectures route all outbound traffic through Azure Firewall "
                    "for inspection and egress policy enforcement. Consider adding egress control."
                ),
                affected_resources=[],
            ))

        # Check: DDoS Protection on public endpoints
        has_ddos = "ddos_protection" in resource_types
        if (has_agw or has_front_door) and not has_ddos:
            findings.append(ValidationFinding(
                severity="info",
                pillar=WafPillar.SECURITY,
                message="No DDoS Protection Plan on public-facing endpoint.",
                recommendation=(
                    "Azure Architecture Center recommends DDoS Protection on Application Gateway "
                    "public IP addresses to mitigate volumetric attacks."
                ),
                affected_resources=[],
            ))

        return findings

    # ── Page annotation ───────────────────────────────────────────

    @staticmethod
    def _annotate_pages(findings: list[ValidationFinding], state: "DiagramState") -> None:
        """Annotate each finding with page number/name from its affected resources."""
        for f in findings:
            if not f.affected_resources:
                continue
            # Find the page from the first affected resource that has one
            for rid in f.affected_resources:
                res = state.resources.get(rid)
                if res and res.properties.get("page"):
                    f.page = res.properties["page"]
                    f.page_name = res.properties.get("page_name", "")
                    break

    # ── Scoring ───────────────────────────────────────────────────

    def _calculate_score(self, findings: list[ValidationFinding]) -> float:
        """Calculate WAF score: 100 minus weighted deductions (critical=15, warning=8, info=3)."""
        if not findings:
            return 100.0

        deductions = 0.0
        for f in findings:
            if f.severity == "critical":
                deductions += 15
            elif f.severity == "warning":
                deductions += 8
            elif f.severity == "info":
                deductions += 3

        return max(0.0, min(100.0, 100.0 - deductions))

    def _generate_summary(self, findings: list[ValidationFinding], score: float) -> str:
        """Generate a human-readable summary with counts by severity and affected pillars."""
        critical = sum(1 for f in findings if f.severity == "critical")
        warnings = sum(1 for f in findings if f.severity == "warning")
        info = sum(1 for f in findings if f.severity == "info")

        pillars_affected = set(f.pillar for f in findings if f.severity in ("critical", "warning"))

        parts = [f"WAF Score: {score:.0f}/100."]
        if critical:
            parts.append(f"{critical} critical issue(s).")
        if warnings:
            parts.append(f"{warnings} warning(s).")
        if info:
            parts.append(f"{info} informational note(s).")
        if pillars_affected:
            pillar_names = ", ".join(
                p.value if isinstance(p, WafPillar) else str(p) for p in sorted(pillars_affected, key=str)
            )
            parts.append(f"Pillars needing attention: {pillar_names}.")

        return " ".join(parts)
