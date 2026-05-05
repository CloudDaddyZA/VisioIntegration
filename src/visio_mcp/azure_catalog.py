"""Comprehensive catalog of Azure resource shapes and their Visio stencil mappings."""

from __future__ import annotations

from pathlib import Path

from .models import AzureServiceCategory, AzureShapeInfo

# Microsoft provides official Azure architecture Visio stencils.
# Stencil file: CnE_CloudV3.1.vssx (Cloud and Enterprise) or individual service stencils.
# Download: https://learn.microsoft.com/en-us/azure/architecture/icons/

# Master names correspond to shape masters in the official Azure Visio stencils.
# The stencil_name values match the master shape names in Microsoft's official stencils.

# ── SVG icon mapping (relative to Icons/ root) ───────────────────
# These map each resource type key to its actual SVG icon file from
# the Azure Public Service Icons pack.
SVG_ICON_MAP: dict[str, str] = {
    "virtual_machine": "compute/10021-icon-service-Virtual-Machine.svg",
    "vm_scale_set": "compute/10034-icon-service-VM-Scale-Sets.svg",
    "app_service": "compute/10035-icon-service-App-Services.svg",
    "app_service_plan": "web/00046-icon-service-App-Service-Plans.svg",
    "function_app": "compute/10029-icon-service-Function-Apps.svg",
    "container_instances": "compute/10104-icon-service-Container-Instances.svg",
    "container_apps": "other/02989-icon-service-Container-Apps-Environments.svg",
    "kubernetes_service": "compute/10023-icon-service-Kubernetes-Services.svg",
    "container_registry": "containers/10105-icon-service-Container-Registries.svg",
    "service_fabric": "containers/10036-icon-service-Service-Fabric-Clusters.svg",
    "batch_account": "containers/10031-icon-service-Batch-Accounts.svg",
    "red_hat_openshift": "containers/03331-icon-service-Azure-Red-Hat-OpenShift.svg",
    "virtual_network": "networking/10061-icon-service-Virtual-Networks.svg",
    "subnet": "networking/02742-icon-service-Subnet.svg",
    "load_balancer": "networking/10062-icon-service-Load-Balancers.svg",
    "application_gateway": "networking/10076-icon-service-Application-Gateways.svg",
    "front_door": "networking/10073-icon-service-Front-Door-and-CDN-Profiles.svg",
    "traffic_manager": "networking/10065-icon-service-Traffic-Manager-Profiles.svg",
    "dns_zone": "networking/10064-icon-service-DNS-Zones.svg",
    "private_endpoint": "other/02579-icon-service-Private-Endpoints.svg",
    "private_link": "networking/00427-icon-service-Private-Link.svg",
    "vpn_gateway": "networking/10063-icon-service-Virtual-Network-Gateways.svg",
    "expressroute": "networking/10079-icon-service-ExpressRoute-Circuits.svg",
    "firewall": "networking/10084-icon-service-Firewalls.svg",
    "nsg": "networking/10067-icon-service-Network-Security-Groups.svg",
    "bastion": "networking/02422-icon-service-Bastions.svg",
    "ddos_protection": "networking/10072-icon-service-DDoS-Protection-Plans.svg",
    "nat_gateway": "networking/10310-icon-service-NAT.svg",
    "cdn_profile": "networking/00056-icon-service-CDN-Profiles.svg",
    "storage_account": "storage/10086-icon-service-Storage-Accounts.svg",
    "blob_storage": "general/10780-icon-service-Blob-Block.svg",
    "data_lake_storage": "storage/10090-icon-service-Data-Lake-Storage-Gen1.svg",
    "managed_disk": "compute/10032-icon-service-Disks.svg",
    "spring_apps": "compute/10370-icon-service-Azure-Spring-Apps.svg",
    "file_share": "storage/10400-icon-service-Azure-Fileshares.svg",
    "netapp_files": "storage/10096-icon-service-Azure-NetApp-Files.svg",
    "sql_database": "databases/10130-icon-service-SQL-Database.svg",
    "sql_managed_instance": "databases/10136-icon-service-SQL-Managed-Instance.svg",
    "azure_sql": "databases/02390-icon-service-Azure-SQL.svg",
    "azure_sql_vm": "databases/10124-icon-service-Azure-SQL-VM.svg",
    "sql_elastic_pool": "databases/10134-icon-service-SQL-Elastic-Pools.svg",
    "cosmos_db": "databases/10121-icon-service-Azure-Cosmos-DB.svg",
    "mysql_database": "databases/10122-icon-service-Azure-Database-MySQL-Server.svg",
    "postgresql_database": "databases/10131-icon-service-Azure-Database-PostgreSQL-Server.svg",
    "mariadb_database": "databases/10123-icon-service-Azure-Database-MariaDB-Server.svg",
    "redis_cache": "databases/10137-icon-service-Cache-Redis.svg",
    "oracle_database": "databases/03490-icon-service-Oracle-Database.svg",
    "key_vault": "security/10245-icon-service-Key-Vaults.svg",
    "defender_for_cloud": "security/10241-icon-service-Microsoft-Defender-for-Cloud.svg",
    "sentinel": "security/10248-icon-service-Azure-Sentinel.svg",
    "managed_identity": "identity/10227-icon-service-Managed-Identities.svg",
    "entra_id": "identity/10231-icon-service-Entra-ID-Protection.svg",
    "app_registration": "identity/10232-icon-service-App-Registrations.svg",
    "api_management": "integration/10042-icon-service-API-Management-Services.svg",
    "logic_app": "integration/02631-icon-service-Logic-Apps.svg",
    "service_bus": "integration/10836-icon-service-Azure-Service-Bus.svg",
    "event_hub": "analytics/00039-icon-service-Event-Hubs.svg",
    "event_grid": "integration/10206-icon-service-Event-Grid-Topics.svg",
    "synapse_analytics": "analytics/00606-icon-service-Azure-Synapse-Analytics.svg",
    "data_factory": "analytics/10126-icon-service-Data-Factories.svg",
    "databricks": "analytics/10787-icon-service-Azure-Databricks.svg",
    "stream_analytics": "analytics/00042-icon-service-Stream-Analytics-Jobs.svg",
    "data_explorer": "analytics/10145-icon-service-Azure-Data-Explorer-Clusters.svg",
    "hdinsight": "analytics/10142-icon-service-HD-Insight-Clusters.svg",
    "analysis_services": "analytics/10148-icon-service-Analysis-Services.svg",
    "power_bi_embedded": "analytics/03332-icon-service-Power-BI-Embedded.svg",
    "event_hub_cluster": "analytics/10149-icon-service-Event-Hub-Clusters.svg",
    "data_lake_analytics": "analytics/10143-icon-service-Data-Lake-Analytics.svg",
    "openai_service": "ai + machine learning/03438-icon-service-Azure-OpenAI.svg",
    "cognitive_services": "ai + machine learning/10162-icon-service-Cognitive-Services.svg",
    "machine_learning": "ai + machine learning/10166-icon-service-Machine-Learning.svg",
    "ai_search": "ai + machine learning/10044-icon-service-Cognitive-Search.svg",
    "ai_studio": "ai + machine learning/03513-icon-service-AI-Studio.svg",
    "bot_service": "ai + machine learning/10165-icon-service-Bot-Services.svg",
    "monitor": "monitor/00001-icon-service-Monitor.svg",
    "log_analytics": "monitor/00009-icon-service-Log-Analytics-Workspaces.svg",
    "application_insights": "monitor/00012-icon-service-Application-Insights.svg",
    "policy": "management + governance/10316-icon-service-Policy.svg",
    "automation_account": "management + governance/00022-icon-service-Automation-Accounts.svg",
    "azure_arc": "management + governance/00756-icon-service-Azure-Arc.svg",
    "advisor": "management + governance/00003-icon-service-Advisor.svg",
    "cost_management": "management + governance/00004-icon-service-Cost-Management-and-Billing.svg",
    "recovery_services_vault": "management + governance/00017-icon-service-Recovery-Services-Vaults.svg",
    "resource_group": "general/10007-icon-service-Resource-Groups.svg",
    "subscription": "general/10002-icon-service-Subscriptions.svg",
    "management_group": "general/10011-icon-service-Management-Groups.svg",
    "devops": "devops/10261-icon-service-Azure-DevOps.svg",
    "iot_hub": "iot/10182-icon-service-IoT-Hub.svg",
    "iot_central": "iot/10184-icon-service-IoT-Central-Applications.svg",
    "user": "identity/10230-icon-service-Users.svg",
    "network_watcher": "networking/10066-icon-service-Network-Watcher.svg",
    "virtual_wan": "networking/10353-icon-service-Virtual-WANs.svg",
    "web_app_firewall": "networking/10362-icon-service-Web-Application-Firewall-Policies(WAF).svg",
    "on_premises": "networking/10070-icon-service-On-Premises-Data-Gateways.svg",
    "internet": "general/10808-icon-service-Globe-Success.svg",
    "static_web_app": "web/01007-icon-service-Static-Apps.svg",
    "signalr": "web/10052-icon-service-SignalR.svg",
    # ── New resource types (grounded from Azure GitHub org review) ──
    # Networking – advanced
    "route_table": "networking/10082-icon-service-Route-Tables.svg",
    "private_link_service": "networking/00427-icon-service-Private-Link.svg",
    "ip_group": "networking/10351-icon-service-IP-Groups.svg",
    "public_ip": "networking/10069-icon-service-Public-IP-Addresses.svg",
    "service_endpoint": "networking/10068-icon-service-Service-Endpoint-Policies.svg",
    # Containers – advanced
    "container_app_environment": "other/02989-icon-service-Container-Apps-Environments.svg",
    # Data – advanced
    "purview": "management + governance/00011-icon-service-Compliance.svg",
    "data_catalog": "analytics/10155-icon-service-Data-Catalog.svg",
    "data_share": "analytics/02807-icon-service-Data-Shares.svg",
    # Integration – advanced
    "event_grid_domain": "integration/10206-icon-service-Event-Grid-Topics.svg",
    "event_grid_system_topic": "integration/10206-icon-service-Event-Grid-Topics.svg",
    # Management – advanced
    "blueprint": "management + governance/00006-icon-service-Blueprints.svg",
    "managed_grafana": "monitor/03422-icon-service-Azure-Managed-Grafana.svg",
    "action_group": "monitor/10005-icon-service-Action-Groups.svg",
    "alert_rule": "monitor/10013-icon-service-Alerts.svg",
    "diagnostic_setting": "monitor/00001-icon-service-Monitor.svg",
    # Security – advanced
    "firewall_policy": "networking/10084-icon-service-Firewalls.svg",
    "application_security_group": "networking/10082-icon-service-Route-Tables.svg",
    # DevOps – advanced
    "github_actions": "devops/10261-icon-service-Azure-DevOps.svg",
    "load_testing": "devops/10261-icon-service-Azure-DevOps.svg",
    # IoT – advanced
    "iot_edge": "iot/10186-icon-service-Azure-IoT-Edge.svg",
    "digital_twins": "iot/10190-icon-service-Digital-Twins.svg",
    "time_series_insights": "iot/10188-icon-service-Time-Series-Insights-Environments.svg",
    # Migration
    "migrate": "migrate/10310-icon-service-Azure-Migrate.svg",
    "database_migration_service": "databases/10139-icon-service-Azure-Database-Migration-Services.svg",
    # Health / Specialized
    "api_for_fhir": "integration/10042-icon-service-API-Management-Services.svg",
    "chaos_studio": "management + governance/00022-icon-service-Automation-Accounts.svg",
    # Storage – queue
    "queue_storage": "general/10840-icon-service-Storage-Queue.svg",
    # Virtual Desktop
    "virtual_desktop": "other/00327-icon-service-Azure-Virtual-Desktop.svg",
}

# ── Additional icon packs (relative to stencils/ root) ───────────

# Microsoft 365 icons
_M365_TEAMS = "M365_Icons/Teams Purple/48x48 Dark Purple Icon"
_M365_BLUE = "M365_Icons/Microsoft Blue/48x48 Dark Blue Icon"
_M365_PLANNER = "M365_Icons/Planner Green/48x48 SVG Icons"
_M365_PROJECT = "M365_Icons/Project Green/48x48 SVG Icons"
_M365_SHAREPOINT = "M365_Icons/SharePoint Teal/48x48 SVG Icon"
M365_ICON_MAP: dict[str, str] = {
    # Microsoft Teams
    "m365_teams": f"{_M365_TEAMS}/People Team.svg",
    "m365_teams_chat": f"{_M365_TEAMS}/Chat.svg",
    "m365_teams_call": f"{_M365_TEAMS}/Call.svg",
    "m365_teams_video": f"{_M365_TEAMS}/Video.svg",
    "m365_teams_bot": f"{_M365_TEAMS}/Bot.svg",
    "m365_teams_calendar": f"{_M365_TEAMS}/Calendar Month.svg",
    "m365_teams_apps": f"{_M365_TEAMS}/Apps.svg",
    "m365_teams_channels": f"{_M365_TEAMS}/Chat Multiple.svg",
    # SharePoint
    "m365_sharepoint": f"{_M365_SHAREPOINT}/Organization_Dark.svg",
    # Exchange / Outlook
    "m365_exchange": f"{_M365_BLUE}/Mail.svg",
    "m365_outlook": f"{_M365_BLUE}/Mail.svg",
    # OneDrive
    "m365_onedrive": f"{_M365_BLUE}/Cloud.svg",
    # Microsoft 365 generic
    "m365": f"{_M365_BLUE}/Globe.svg",
    "m365_admin": f"{_M365_BLUE}/Settings Cog Multiple.svg",
    "m365_copilot": f"{_M365_BLUE}/Lightbulb Checkmark.svg",
    # Word / Excel / PowerPoint / OneNote
    "m365_word": f"{_M365_BLUE}/Document.svg",
    "m365_excel": f"{_M365_BLUE}/Data Bar Vertical.svg",
    "m365_powerpoint": f"{_M365_BLUE}/Slide Layout.svg",
    "m365_onenote": f"{_M365_BLUE}/Notebook.svg",
    # Planner
    "m365_planner": f"{_M365_PLANNER}/Clipboard_Task_List_Dark.svg",
    # Project
    "m365_project": f"{_M365_PROJECT}/Text_Bullet_List_Dark.svg",
    # Stream
    "m365_stream": f"{_M365_BLUE}/Filmstrip Play.svg",
    # Viva
    "m365_viva": f"{_M365_BLUE}/People Community.svg",
    "m365_viva_learning": f"{_M365_BLUE}/Hat Graduation.svg",
    "m365_viva_engage": f"{_M365_BLUE}/People Community.svg",
    # Defender for M365
    "m365_defender": f"{_M365_BLUE}/Shield Error.svg",
    "m365_security": f"{_M365_BLUE}/Lock Shield.svg",
    # Intune
    "m365_intune": f"{_M365_BLUE}/Phone Laptop.svg",
    # Bookings
    "m365_bookings": f"{_M365_BLUE}/Calendar Month.svg",
    # Forms
    "m365_forms": f"{_M365_BLUE}/Checkmark Circle.svg",
    # Power Pages (M365 context)
    "m365_power_pages": f"{_M365_BLUE}/Globe.svg",
    # Generic building/cloud
    "m365_building": f"{_M365_BLUE}/Building.svg",
    "m365_cloud": f"{_M365_BLUE}/Building Cloud.svg",
    # Support / service desk
    "m365_support": f"{_M365_BLUE}/Headset.svg",
}

# Microsoft Entra icons
_ENTRA_ROOT = "Entra_Icons/Microsoft Entra architecture icons - Oct 2023/Microsoft Entra color icons SVG"
ENTRA_ICON_MAP: dict[str, str] = {
    "entra_id_protection": f"{_ENTRA_ROOT}/Microsoft Entra ID color icon.svg",
    "entra_id_governance": f"{_ENTRA_ROOT}/Microsoft Entra ID Governance color icon.svg",
    "entra_internet_access": f"{_ENTRA_ROOT}/Microsoft Entra Internet Access color icon.svg",
    "entra_private_access": f"{_ENTRA_ROOT}/Microsoft Entra Private Access color icon.svg",
    "entra_verified_id": f"{_ENTRA_ROOT}/Microsoft Entra Verified ID color icon.svg",
    "entra_workload_id": f"{_ENTRA_ROOT}/Microsoft Entra Workload ID color icon.svg",
    "entra_product_family": f"{_ENTRA_ROOT}/Microsoft Entra Product Family.svg",
}

# Microsoft Fabric icons (48px item/color variants)
_FABRIC_ROOT = "Fabric_Icons/v6.1.0/package/dist/svg"
FABRIC_ICON_MAP: dict[str, str] = {
    # Workload item icons
    "fabric_lakehouse": f"{_FABRIC_ROOT}/lakehouse_48_item.svg",
    "fabric_data_warehouse": f"{_FABRIC_ROOT}/data_warehouse_48_item.svg",
    "fabric_pipeline": f"{_FABRIC_ROOT}/pipeline_48_item.svg",
    "fabric_notebook": f"{_FABRIC_ROOT}/notebook_48_item.svg",
    "fabric_eventhouse": f"{_FABRIC_ROOT}/event_house_48_item.svg",
    "fabric_eventstream": f"{_FABRIC_ROOT}/eventstream_48_item.svg",
    "fabric_dashboard": f"{_FABRIC_ROOT}/dashboard_48_item.svg",
    "fabric_report": f"{_FABRIC_ROOT}/report_48_item.svg",
    "fabric_dataflow": f"{_FABRIC_ROOT}/dataflow_48_item.svg",
    "fabric_semantic_model": f"{_FABRIC_ROOT}/semantic_model_48_item.svg",
    "fabric_kql_database": f"{_FABRIC_ROOT}/kql_database_48_item.svg",
    "fabric_sql_database": f"{_FABRIC_ROOT}/sql_database_48_item.svg",
    "fabric_real_time_dashboard": f"{_FABRIC_ROOT}/real_time_dashboard_48_item.svg",
    "fabric_data_agent": f"{_FABRIC_ROOT}/data_agent_48_item.svg",
    "fabric_data_factory": f"{_FABRIC_ROOT}/data_factory_48_item.svg",
    "fabric_model": f"{_FABRIC_ROOT}/model_48_item.svg",
    "fabric_scorecard": f"{_FABRIC_ROOT}/scorecard_48_item.svg",
    "fabric_paginated_report": f"{_FABRIC_ROOT}/paginated_report_48_item.svg",
    # Workload color icons
    "fabric": f"{_FABRIC_ROOT}/fabric_48_color.svg",
    "fabric_power_bi": f"{_FABRIC_ROOT}/power_bi_48_color.svg",
    "fabric_copilot": f"{_FABRIC_ROOT}/copilot_48_color.svg",
    "fabric_purview": f"{_FABRIC_ROOT}/purview_48_color.svg",
    "fabric_onelake": f"{_FABRIC_ROOT}/one_lake_48_color.svg",
    "fabric_data_engineering": f"{_FABRIC_ROOT}/data_engineering_48_color.svg",
    "fabric_data_science": f"{_FABRIC_ROOT}/data_science_48_color.svg",
    "fabric_real_time_intelligence": f"{_FABRIC_ROOT}/real_time_intelligence_48_color.svg",
    "fabric_databases": f"{_FABRIC_ROOT}/databases_48_color.svg",
    "fabric_graph_intelligence": f"{_FABRIC_ROOT}/graph_intelligence_48_color.svg",
}

# Merge all icon maps so the Visio engine can look up any resource key
ALL_ICON_MAPS: dict[str, str] = {**SVG_ICON_MAP}
# Entra and Fabric icons use paths relative to stencils/ (not Icons/)
# so we prefix with "../" to resolve from the Icons/ root
_STENCILS_ROOT = Path(__file__).parent / "stencils"
for _map in (M365_ICON_MAP, ENTRA_ICON_MAP, FABRIC_ICON_MAP):
    for _key, _relpath in _map.items():
        ALL_ICON_MAPS[_key] = f"../../{_relpath}"  # relative from Icons/ to stencils/

# Default icons root relative to this package
_DEFAULT_ICONS_ROOT = Path(__file__).parent / "stencils" / "Azure_Public_Service_Icons" / "Icons"

# ── Common aliases ────────────────────────────────────────────────
# AI agents and users naturally use abbreviations like "aks" or "apim".
# This map resolves them to the canonical catalog key.
RESOURCE_ALIASES: dict[str, str] = {
    "aks": "kubernetes_service",
    "apim": "api_management",
    "vm": "virtual_machine",
    "vmss": "vm_scale_set",
    "vnet": "virtual_network",
    "adx": "data_explorer",
    "acr": "container_registry",
    "appgw": "application_gateway",
    "agw": "application_gateway",
    "afd": "front_door",
    "waf": "web_app_firewall",
    "nsg": "nsg",
    "pip": "public_ip",
    "sql": "sql_database",
    "cosmosdb": "cosmos_db",
    "cosmos": "cosmos_db",
    "postgres": "postgresql_database",
    "mysql": "mysql_database",
    "redis": "redis_cache",
    "mariadb": "mariadb_database",
    "keyvault": "key_vault",
    "kv": "key_vault",
    "adf": "data_factory",
    "asa": "stream_analytics",
    "openai": "openai_service",
    "aml": "machine_learning",
    "aci": "container_instances",
    "aca": "container_apps",
    "asb": "service_bus",
    "aeh": "event_hub",
    "aeg": "event_grid",
    "la": "log_analytics",
    "appinsights": "application_insights",
    "ai_search": "ai_search",
    "cognitive": "cognitive_services",
    # ── New aliases (grounded from Azure GitHub org review) ──
    "rt": "route_table",
    "pls": "private_link_service",
    "pip": "public_ip",
    "cae": "container_app_environment",
    "purview": "purview",
    "egdt": "event_grid_domain",
    "grafana": "managed_grafana",
    "dte": "digital_twins",
    "tsi": "time_series_insights",
    "dms": "database_migration_service",
    "chaos": "chaos_studio",
    "fhir": "api_for_fhir",
    "iot_edge": "iot_edge",
    "blueprint": "blueprint",
    "asg": "application_security_group",
}


def resolve_alias(resource_type: str) -> str:
    """Resolve a resource type alias to its canonical catalog key.

    Handles common abbreviations like 'aks' -> 'kubernetes_service',
    'apim' -> 'api_management', 'vm' -> 'virtual_machine', etc.
    Returns the original key unchanged if no alias match is found.
    """
    return RESOURCE_ALIASES.get(resource_type.lower(), resource_type)


AZURE_SHAPE_CATALOG: dict[str, AzureShapeInfo] = {
    # ── Compute ───────────────────────────────────────────────────
    "virtual_machine": AzureShapeInfo(
        key="virtual_machine",
        display_name="Virtual Machine",
        category=AzureServiceCategory.COMPUTE,
        stencil_name="Virtual Machine",
        stencil_file="AzureCompute.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Use Availability Sets or Zones for HA. Configure health probes.",
            "Security": "Enable Azure Defender. Use managed disks with encryption. Apply NSGs.",
            "Cost Optimization": "Right-size VMs. Use Reserved Instances or Spot VMs for non-critical workloads.",
            "Operational Excellence": "Enable boot diagnostics and Azure Monitor agent.",
            "Performance Efficiency": "Select appropriate VM family. Use Accelerated Networking.",
        },
    ),
    "vm_scale_set": AzureShapeInfo(
        key="vm_scale_set",
        display_name="Virtual Machine Scale Set",
        category=AzureServiceCategory.COMPUTE,
        stencil_name="VM Scale Set",
        stencil_file="AzureCompute.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Deploy across Availability Zones. Configure health probes and auto-repair.",
            "Performance Efficiency": "Configure autoscale rules based on metrics.",
        },
    ),
    "app_service": AzureShapeInfo(
        key="app_service",
        display_name="App Service",
        category=AzureServiceCategory.WEB,
        stencil_name="App Service",
        stencil_file="AzureWeb.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Use Standard tier or higher. Deploy to multiple regions with Traffic Manager.",
            "Security": "Enable managed identity. Use VNet integration. Configure access restrictions.",
            "Cost Optimization": "Use consumption or shared plans for dev/test. Auto-scale production.",
            "Performance Efficiency": "Enable auto-scale. Use deployment slots for zero-downtime deploys.",
        },
    ),
    "app_service_plan": AzureShapeInfo(
        key="app_service_plan",
        display_name="App Service Plan",
        category=AzureServiceCategory.WEB,
        stencil_name="App Service Plan",
        stencil_file="AzureWeb.vssx",
        icon_color="#0078D4",
    ),
    "function_app": AzureShapeInfo(
        key="function_app",
        display_name="Function App",
        category=AzureServiceCategory.COMPUTE,
        stencil_name="Function App",
        stencil_file="AzureCompute.vssx",
        icon_color="#FFB900",
        waf_considerations={
            "Reliability": "Use Premium or Dedicated plan for critical workloads. Configure retry policies.",
            "Security": "Use managed identity. Secure function keys. Enable VNet integration.",
            "Cost Optimization": "Use Consumption plan for sporadic workloads. Monitor execution counts.",
        },
    ),
    "spring_apps": AzureShapeInfo(
        key="spring_apps",
        display_name="Azure Spring Apps",
        category=AzureServiceCategory.COMPUTE,
        stencil_name="Azure Spring Apps",
        stencil_file="AzureCompute.vssx",
        icon_color="#6DB33F",
    ),
    "container_instances": AzureShapeInfo(
        key="container_instances",
        display_name="Container Instances",
        category=AzureServiceCategory.CONTAINERS,
        stencil_name="Container Instances",
        stencil_file="AzureContainers.vssx",
        icon_color="#0078D4",
    ),
    "container_apps": AzureShapeInfo(
        key="container_apps",
        display_name="Container Apps",
        category=AzureServiceCategory.CONTAINERS,
        stencil_name="Container Apps",
        stencil_file="AzureContainers.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Configure min replicas > 0 for production. Use revision management.",
            "Security": "Use managed identity. Enable ingress access controls. Scan container images.",
            "Performance Efficiency": "Configure scale rules (HTTP, KEDA).",
        },
    ),
    "kubernetes_service": AzureShapeInfo(
        key="kubernetes_service",
        display_name="Azure Kubernetes Service",
        category=AzureServiceCategory.CONTAINERS,
        stencil_name="Kubernetes Service",
        stencil_file="AzureContainers.vssx",
        icon_color="#326CE5",
        waf_considerations={
            "Reliability": "Use multiple node pools across AZs. Configure PodDisruptionBudgets.",
            "Security": "Enable Azure Policy for AKS. Use private clusters. Enable Defender for Containers.",
            "Cost Optimization": "Use spot node pools for interruptible workloads. Right-size nodes.",
            "Operational Excellence": "Enable Container Insights. Use GitOps with Flux.",
            "Performance Efficiency": "Use cluster autoscaler and HPA. Select appropriate VM SKUs.",
        },
    ),
    "container_registry": AzureShapeInfo(
        key="container_registry",
        display_name="Container Registry",
        category=AzureServiceCategory.CONTAINERS,
        stencil_name="Container Registry",
        stencil_file="AzureContainers.vssx",
        icon_color="#0078D4",
    ),
    "service_fabric": AzureShapeInfo(
        key="service_fabric",
        display_name="Service Fabric Cluster",
        category=AzureServiceCategory.CONTAINERS,
        stencil_name="Service Fabric Cluster",
        stencil_file="AzureContainers.vssx",
        icon_color="#0078D4",
    ),
    "batch_account": AzureShapeInfo(
        key="batch_account",
        display_name="Batch Account",
        category=AzureServiceCategory.COMPUTE,
        stencil_name="Batch Account",
        stencil_file="AzureCompute.vssx",
        icon_color="#0078D4",
    ),
    "red_hat_openshift": AzureShapeInfo(
        key="red_hat_openshift",
        display_name="Azure Red Hat OpenShift",
        category=AzureServiceCategory.CONTAINERS,
        stencil_name="Azure Red Hat OpenShift",
        stencil_file="AzureContainers.vssx",
        icon_color="#EE0000",
    ),

    # ── Networking ────────────────────────────────────────────────
    "virtual_network": AzureShapeInfo(
        key="virtual_network",
        display_name="Virtual Network",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Virtual Network",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Use NSGs on all subnets. Enable DDoS Protection Standard for public-facing VNets.",
            "Reliability": "Plan address space carefully to avoid overlaps. Use VNet peering for connectivity.",
        },
    ),
    "subnet": AzureShapeInfo(
        key="subnet",
        display_name="Subnet",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Subnet",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "load_balancer": AzureShapeInfo(
        key="load_balancer",
        display_name="Load Balancer",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Load Balancer",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Use Standard SKU with zone-redundant frontend. Configure health probes.",
            "Performance Efficiency": "Choose appropriate distribution mode.",
        },
    ),
    "application_gateway": AzureShapeInfo(
        key="application_gateway",
        display_name="Application Gateway",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Application Gateway",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Enable WAF v2 with OWASP rules. Use TLS termination.",
            "Reliability": "Use v2 SKU with autoscaling. Deploy across zones.",
            "Performance Efficiency": "Enable connection draining. Configure autoscaling.",
        },
    ),
    "front_door": AzureShapeInfo(
        key="front_door",
        display_name="Front Door",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Front Door",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Global load balancing with instant failover. Use health probes.",
            "Security": "Enable WAF policies. Use Private Link origins.",
            "Performance Efficiency": "Enable caching. Use compression.",
        },
    ),
    "traffic_manager": AzureShapeInfo(
        key="traffic_manager",
        display_name="Traffic Manager",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Traffic Manager",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "dns_zone": AzureShapeInfo(
        key="dns_zone",
        display_name="DNS Zone",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="DNS Zone",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "private_endpoint": AzureShapeInfo(
        key="private_endpoint",
        display_name="Private Endpoint",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Private Endpoint",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "private_link": AzureShapeInfo(
        key="private_link",
        display_name="Private Link Service",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Private Link Service",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "vpn_gateway": AzureShapeInfo(
        key="vpn_gateway",
        display_name="VPN Gateway",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="VPN Gateway",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "expressroute": AzureShapeInfo(
        key="expressroute",
        display_name="ExpressRoute Circuit",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="ExpressRoute Circuit",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "firewall": AzureShapeInfo(
        key="firewall",
        display_name="Azure Firewall",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Azure Firewall",
        stencil_file="AzureNetworking.vssx",
        icon_color="#FF4F1F",
        waf_considerations={
            "Security": "Use Firewall Premium for TLS inspection. Centralize policies with Firewall Manager.",
            "Reliability": "Deploy across Availability Zones. Use forced tunneling for compliance.",
        },
    ),
    "nsg": AzureShapeInfo(
        key="nsg",
        display_name="Network Security Group",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Network Security Group",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "bastion": AzureShapeInfo(
        key="bastion",
        display_name="Azure Bastion",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Azure Bastion",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "ddos_protection": AzureShapeInfo(
        key="ddos_protection",
        display_name="DDoS Protection Plan",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="DDoS Protection Plan",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "nat_gateway": AzureShapeInfo(
        key="nat_gateway",
        display_name="NAT Gateway",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="NAT Gateway",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "cdn_profile": AzureShapeInfo(
        key="cdn_profile",
        display_name="CDN Profile",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="CDN Profile",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "network_watcher": AzureShapeInfo(
        key="network_watcher",
        display_name="Network Watcher",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Network Watcher",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "virtual_wan": AzureShapeInfo(
        key="virtual_wan",
        display_name="Virtual WAN",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Virtual WAN",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "web_app_firewall": AzureShapeInfo(
        key="web_app_firewall",
        display_name="Web Application Firewall",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Web Application Firewall",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),

    # ── Storage ───────────────────────────────────────────────────
    "storage_account": AzureShapeInfo(
        key="storage_account",
        display_name="Storage Account",
        category=AzureServiceCategory.STORAGE,
        stencil_name="Storage Account",
        stencil_file="AzureStorage.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Use GRS/RA-GRS for critical data. Enable soft delete and versioning.",
            "Security": "Disable public blob access. Use private endpoints. Enable encryption.",
            "Cost Optimization": "Use lifecycle management policies. Choose correct access tier.",
        },
    ),
    "blob_storage": AzureShapeInfo(
        key="blob_storage",
        display_name="Blob Storage",
        category=AzureServiceCategory.STORAGE,
        stencil_name="Blob Storage",
        stencil_file="AzureStorage.vssx",
        icon_color="#0078D4",
    ),
    "data_lake_storage": AzureShapeInfo(
        key="data_lake_storage",
        display_name="Data Lake Storage Gen2",
        category=AzureServiceCategory.STORAGE,
        stencil_name="Data Lake Storage",
        stencil_file="AzureStorage.vssx",
        icon_color="#0078D4",
    ),
    "managed_disk": AzureShapeInfo(
        key="managed_disk",
        display_name="Managed Disk",
        category=AzureServiceCategory.STORAGE,
        stencil_name="Managed Disk",
        stencil_file="AzureStorage.vssx",
        icon_color="#0078D4",
    ),
    "file_share": AzureShapeInfo(
        key="file_share",
        display_name="Azure Files",
        category=AzureServiceCategory.STORAGE,
        stencil_name="Azure Files",
        stencil_file="AzureStorage.vssx",
        icon_color="#0078D4",
    ),
    "netapp_files": AzureShapeInfo(
        key="netapp_files",
        display_name="Azure NetApp Files",
        category=AzureServiceCategory.STORAGE,
        stencil_name="Azure NetApp Files",
        stencil_file="AzureStorage.vssx",
        icon_color="#0078D4",
    ),

    # ── Databases ─────────────────────────────────────────────────
    "sql_database": AzureShapeInfo(
        key="sql_database",
        display_name="Azure SQL Database",
        category=AzureServiceCategory.DATABASES,
        stencil_name="SQL Database",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Use auto-failover groups. Enable zone redundancy. Configure backup retention.",
            "Security": "Enable TDE and Always Encrypted. Use AAD authentication. Configure firewall rules.",
            "Cost Optimization": "Use elastic pools for multiple DBs. Consider serverless tier.",
            "Performance Efficiency": "Use read replicas. Enable automatic tuning.",
        },
    ),
    "sql_managed_instance": AzureShapeInfo(
        key="sql_managed_instance",
        display_name="SQL Managed Instance",
        category=AzureServiceCategory.DATABASES,
        stencil_name="SQL Managed Instance",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
    ),
    "cosmos_db": AzureShapeInfo(
        key="cosmos_db",
        display_name="Cosmos DB",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Azure Cosmos DB",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Enable multi-region writes. Configure automatic failover.",
            "Security": "Use private endpoints. Disable key-based access, prefer AAD/RBAC.",
            "Cost Optimization": "Use autoscale throughput. Choose correct consistency level.",
            "Performance Efficiency": "Design partition keys carefully. Use change feed for reactive patterns.",
        },
    ),
    "mysql_database": AzureShapeInfo(
        key="mysql_database",
        display_name="Azure Database for MySQL",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Azure Database for MySQL",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
    ),
    "postgresql_database": AzureShapeInfo(
        key="postgresql_database",
        display_name="Azure Database for PostgreSQL",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Azure Database for PostgreSQL",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
    ),
    "redis_cache": AzureShapeInfo(
        key="redis_cache",
        display_name="Azure Cache for Redis",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Azure Cache for Redis",
        stencil_file="AzureDatabases.vssx",
        icon_color="#D92B2B",
        waf_considerations={
            "Reliability": "Use Premium tier with zone redundancy and data persistence.",
            "Security": "Use private endpoints. Disable non-TLS connections.",
        },
    ),
    "azure_sql": AzureShapeInfo(
        key="azure_sql",
        display_name="Azure SQL",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Azure SQL",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
    ),
    "azure_sql_vm": AzureShapeInfo(
        key="azure_sql_vm",
        display_name="SQL Server on Azure VM",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Azure SQL VM",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
    ),
    "sql_elastic_pool": AzureShapeInfo(
        key="sql_elastic_pool",
        display_name="SQL Elastic Pool",
        category=AzureServiceCategory.DATABASES,
        stencil_name="SQL Elastic Pool",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
    ),
    "mariadb_database": AzureShapeInfo(
        key="mariadb_database",
        display_name="Azure Database for MariaDB",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Azure Database for MariaDB",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
    ),
    "oracle_database": AzureShapeInfo(
        key="oracle_database",
        display_name="Oracle Database@Azure",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Oracle Database",
        stencil_file="AzureDatabases.vssx",
        icon_color="#C74634",
    ),

    # ── Security ──────────────────────────────────────────────────
    "key_vault": AzureShapeInfo(
        key="key_vault",
        display_name="Key Vault",
        category=AzureServiceCategory.SECURITY,
        stencil_name="Key Vault",
        stencil_file="AzureSecurity.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Use RBAC access model. Enable soft-delete and purge protection. Use private endpoints.",
            "Reliability": "Key Vault is zone-redundant by default. Use separate vaults per environment.",
        },
    ),
    "defender_for_cloud": AzureShapeInfo(
        key="defender_for_cloud",
        display_name="Microsoft Defender for Cloud",
        category=AzureServiceCategory.SECURITY,
        stencil_name="Microsoft Defender for Cloud",
        stencil_file="AzureSecurity.vssx",
        icon_color="#0078D4",
    ),
    "sentinel": AzureShapeInfo(
        key="sentinel",
        display_name="Microsoft Sentinel",
        category=AzureServiceCategory.SECURITY,
        stencil_name="Microsoft Sentinel",
        stencil_file="AzureSecurity.vssx",
        icon_color="#0078D4",
    ),
    "managed_identity": AzureShapeInfo(
        key="managed_identity",
        display_name="Managed Identity",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="Managed Identity",
        stencil_file="AzureIdentity.vssx",
        icon_color="#0078D4",
    ),

    # ── Identity ──────────────────────────────────────────────────
    "entra_id": AzureShapeInfo(
        key="entra_id",
        display_name="Microsoft Entra ID",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="Azure Active Directory",
        stencil_file="AzureIdentity.vssx",
        icon_color="#0078D4",
    ),
    "app_registration": AzureShapeInfo(
        key="app_registration",
        display_name="App Registration",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="App Registration",
        stencil_file="AzureIdentity.vssx",
        icon_color="#0078D4",
    ),

    # ── Integration ───────────────────────────────────────────────
    "api_management": AzureShapeInfo(
        key="api_management",
        display_name="API Management",
        category=AzureServiceCategory.INTEGRATION,
        stencil_name="API Management",
        stencil_file="AzureIntegration.vssx",
        icon_color="#68217A",
        waf_considerations={
            "Security": "Use OAuth2/JWT validation policies. Enable rate limiting. Use VNet integration.",
            "Performance Efficiency": "Enable response caching. Use backend pools for load distribution.",
        },
    ),
    "logic_app": AzureShapeInfo(
        key="logic_app",
        display_name="Logic App",
        category=AzureServiceCategory.INTEGRATION,
        stencil_name="Logic App",
        stencil_file="AzureIntegration.vssx",
        icon_color="#0078D4",
    ),
    "service_bus": AzureShapeInfo(
        key="service_bus",
        display_name="Service Bus",
        category=AzureServiceCategory.MESSAGING,
        stencil_name="Service Bus",
        stencil_file="AzureIntegration.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Use Premium tier with zone redundancy. Enable geo-disaster recovery.",
            "Security": "Use managed identity for access. Enable private endpoints.",
        },
    ),
    "event_hub": AzureShapeInfo(
        key="event_hub",
        display_name="Event Hubs",
        category=AzureServiceCategory.MESSAGING,
        stencil_name="Event Hubs",
        stencil_file="AzureIntegration.vssx",
        icon_color="#0078D4",
    ),
    "event_grid": AzureShapeInfo(
        key="event_grid",
        display_name="Event Grid",
        category=AzureServiceCategory.MESSAGING,
        stencil_name="Event Grid",
        stencil_file="AzureIntegration.vssx",
        icon_color="#0078D4",
    ),

    # ── Analytics ─────────────────────────────────────────────────
    "synapse_analytics": AzureShapeInfo(
        key="synapse_analytics",
        display_name="Azure Synapse Analytics",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Azure Synapse Analytics",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),
    "data_factory": AzureShapeInfo(
        key="data_factory",
        display_name="Data Factory",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Data Factory",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),
    "databricks": AzureShapeInfo(
        key="databricks",
        display_name="Azure Databricks",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Azure Databricks",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#FF3621",
    ),
    "stream_analytics": AzureShapeInfo(
        key="stream_analytics",
        display_name="Stream Analytics",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Stream Analytics",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),
    "data_explorer": AzureShapeInfo(
        key="data_explorer",
        display_name="Azure Data Explorer",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Azure Data Explorer Cluster",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Use multiple cluster replicas. Configure hot/warm cache policies.",
            "Security": "Enable managed identity. Use private endpoints. Restrict network access.",
            "Cost Optimization": "Right-size cluster SKU. Use optimized autoscale. Archive cold data.",
            "Performance Efficiency": "Tune ingestion batching. Use materialized views for hot queries.",
        },
    ),
    "hdinsight": AzureShapeInfo(
        key="hdinsight",
        display_name="HDInsight",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="HDInsight Cluster",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),
    "analysis_services": AzureShapeInfo(
        key="analysis_services",
        display_name="Analysis Services",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Analysis Services",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),
    "power_bi_embedded": AzureShapeInfo(
        key="power_bi_embedded",
        display_name="Power BI Embedded",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Power BI Embedded",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#F2C811",
    ),
    "event_hub_cluster": AzureShapeInfo(
        key="event_hub_cluster",
        display_name="Event Hub Cluster",
        category=AzureServiceCategory.MESSAGING,
        stencil_name="Event Hub Cluster",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),
    "data_lake_analytics": AzureShapeInfo(
        key="data_lake_analytics",
        display_name="Data Lake Analytics",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Data Lake Analytics",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),

    # ── AI + Machine Learning ─────────────────────────────────────
    "openai_service": AzureShapeInfo(
        key="openai_service",
        display_name="Azure OpenAI Service",
        category=AzureServiceCategory.AI_ML,
        stencil_name="Azure OpenAI",
        stencil_file="AzureAI.vssx",
        icon_color="#0078D4",
    ),
    "cognitive_services": AzureShapeInfo(
        key="cognitive_services",
        display_name="Azure AI Services",
        category=AzureServiceCategory.AI_ML,
        stencil_name="Cognitive Services",
        stencil_file="AzureAI.vssx",
        icon_color="#0078D4",
    ),
    "machine_learning": AzureShapeInfo(
        key="machine_learning",
        display_name="Azure Machine Learning",
        category=AzureServiceCategory.AI_ML,
        stencil_name="Machine Learning",
        stencil_file="AzureAI.vssx",
        icon_color="#0078D4",
    ),
    "ai_search": AzureShapeInfo(
        key="ai_search",
        display_name="Azure AI Search",
        category=AzureServiceCategory.AI_ML,
        stencil_name="Azure AI Search",
        stencil_file="AzureAI.vssx",
        icon_color="#0078D4",
    ),
    "ai_studio": AzureShapeInfo(
        key="ai_studio",
        display_name="Azure AI Studio",
        category=AzureServiceCategory.AI_ML,
        stencil_name="AI Studio",
        stencil_file="AzureAI.vssx",
        icon_color="#0078D4",
    ),
    "bot_service": AzureShapeInfo(
        key="bot_service",
        display_name="Bot Service",
        category=AzureServiceCategory.AI_ML,
        stencil_name="Bot Service",
        stencil_file="AzureAI.vssx",
        icon_color="#0078D4",
    ),

    # ── Management + Governance ───────────────────────────────────
    "monitor": AzureShapeInfo(
        key="monitor",
        display_name="Azure Monitor",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Azure Monitor",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "log_analytics": AzureShapeInfo(
        key="log_analytics",
        display_name="Log Analytics Workspace",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Log Analytics Workspace",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "application_insights": AzureShapeInfo(
        key="application_insights",
        display_name="Application Insights",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Application Insights",
        stencil_file="AzureManagement.vssx",
        icon_color="#68217A",
    ),
    "policy": AzureShapeInfo(
        key="policy",
        display_name="Azure Policy",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Azure Policy",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "automation_account": AzureShapeInfo(
        key="automation_account",
        display_name="Automation Account",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Automation Account",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "azure_arc": AzureShapeInfo(
        key="azure_arc",
        display_name="Azure Arc",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Azure Arc",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "advisor": AzureShapeInfo(
        key="advisor",
        display_name="Azure Advisor",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Azure Advisor",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "cost_management": AzureShapeInfo(
        key="cost_management",
        display_name="Cost Management + Billing",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Cost Management",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "recovery_services_vault": AzureShapeInfo(
        key="recovery_services_vault",
        display_name="Recovery Services Vault",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Recovery Services Vault",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "resource_group": AzureShapeInfo(
        key="resource_group",
        display_name="Resource Group",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Resource Group",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "subscription": AzureShapeInfo(
        key="subscription",
        display_name="Subscription",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Subscription",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),
    "management_group": AzureShapeInfo(
        key="management_group",
        display_name="Management Group",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Management Group",
        stencil_file="AzureManagement.vssx",
        icon_color="#0078D4",
    ),

    # ── DevOps ────────────────────────────────────────────────────
    "devops": AzureShapeInfo(
        key="devops",
        display_name="Azure DevOps",
        category=AzureServiceCategory.DEVOPS,
        stencil_name="Azure DevOps",
        stencil_file="AzureDevOps.vssx",
        icon_color="#0078D4",
    ),

    # ── IoT ───────────────────────────────────────────────────────
    "iot_hub": AzureShapeInfo(
        key="iot_hub",
        display_name="IoT Hub",
        category=AzureServiceCategory.IOT,
        stencil_name="IoT Hub",
        stencil_file="AzureIoT.vssx",
        icon_color="#0078D4",
    ),
    "iot_central": AzureShapeInfo(
        key="iot_central",
        display_name="IoT Central",
        category=AzureServiceCategory.IOT,
        stencil_name="IoT Central",
        stencil_file="AzureIoT.vssx",
        icon_color="#0078D4",
    ),

    # ── General / External ────────────────────────────────────────
    "user": AzureShapeInfo(
        key="user",
        display_name="User / Client",
        category=AzureServiceCategory.GENERAL,
        stencil_name="User",
        stencil_file="AzureGeneral.vssx",
        icon_color="#505050",
    ),
    "on_premises": AzureShapeInfo(
        key="on_premises",
        display_name="On-Premises",
        category=AzureServiceCategory.GENERAL,
        stencil_name="On-Premises",
        stencil_file="AzureGeneral.vssx",
        icon_color="#505050",
    ),
    "internet": AzureShapeInfo(
        key="internet",
        display_name="Internet",
        category=AzureServiceCategory.GENERAL,
        stencil_name="Internet",
        stencil_file="AzureGeneral.vssx",
        icon_color="#505050",
    ),
    "static_web_app": AzureShapeInfo(
        key="static_web_app",
        display_name="Static Web App",
        category=AzureServiceCategory.WEB,
        stencil_name="Static Web App",
        stencil_file="AzureWeb.vssx",
        icon_color="#0078D4",
    ),
    "signalr": AzureShapeInfo(
        key="signalr",
        display_name="Azure SignalR Service",
        category=AzureServiceCategory.WEB,
        stencil_name="SignalR",
        stencil_file="AzureWeb.vssx",
        icon_color="#0078D4",
    ),
    # ── Microsoft Entra (Identity) ────────────────────────────────
    "entra_id_protection": AzureShapeInfo(
        key="entra_id_protection",
        display_name="Microsoft Entra ID",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="Entra ID",
        stencil_file="EntraIcons",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Enable MFA and Conditional Access. Use Privileged Identity Management.",
            "Reliability": "Configure backup authentication methods. Monitor sign-in health.",
        },
    ),
    "entra_id_governance": AzureShapeInfo(
        key="entra_id_governance",
        display_name="Microsoft Entra ID Governance",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="Entra ID Governance",
        stencil_file="EntraIcons",
        icon_color="#0078D4",
    ),
    "entra_internet_access": AzureShapeInfo(
        key="entra_internet_access",
        display_name="Microsoft Entra Internet Access",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="Entra Internet Access",
        stencil_file="EntraIcons",
        icon_color="#0078D4",
    ),
    "entra_private_access": AzureShapeInfo(
        key="entra_private_access",
        display_name="Microsoft Entra Private Access",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="Entra Private Access",
        stencil_file="EntraIcons",
        icon_color="#0078D4",
    ),
    "entra_verified_id": AzureShapeInfo(
        key="entra_verified_id",
        display_name="Microsoft Entra Verified ID",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="Entra Verified ID",
        stencil_file="EntraIcons",
        icon_color="#0078D4",
    ),
    "entra_workload_id": AzureShapeInfo(
        key="entra_workload_id",
        display_name="Microsoft Entra Workload ID",
        category=AzureServiceCategory.IDENTITY,
        stencil_name="Entra Workload ID",
        stencil_file="EntraIcons",
        icon_color="#0078D4",
    ),
    # ── Microsoft Fabric (Analytics) ──────────────────────────────
    "fabric_lakehouse": AzureShapeInfo(
        key="fabric_lakehouse",
        display_name="Fabric Lakehouse",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Lakehouse",
        stencil_file="FabricIcons",
        icon_color="#008572",
        waf_considerations={
            "Performance Efficiency": "Use V-Order optimization. Partition large tables.",
            "Cost Optimization": "Leverage OneLake storage. Use shortcuts to avoid data duplication.",
        },
    ),
    "fabric_data_warehouse": AzureShapeInfo(
        key="fabric_data_warehouse",
        display_name="Fabric Data Warehouse",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Data Warehouse",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_pipeline": AzureShapeInfo(
        key="fabric_pipeline",
        display_name="Fabric Pipeline",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Pipeline",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_notebook": AzureShapeInfo(
        key="fabric_notebook",
        display_name="Fabric Notebook",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Notebook",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_eventhouse": AzureShapeInfo(
        key="fabric_eventhouse",
        display_name="Fabric Eventhouse",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Eventhouse",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_eventstream": AzureShapeInfo(
        key="fabric_eventstream",
        display_name="Fabric Eventstream",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Eventstream",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_dashboard": AzureShapeInfo(
        key="fabric_dashboard",
        display_name="Fabric Dashboard",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Dashboard",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_report": AzureShapeInfo(
        key="fabric_report",
        display_name="Fabric Report",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Report",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_dataflow": AzureShapeInfo(
        key="fabric_dataflow",
        display_name="Fabric Dataflow",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Dataflow",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_semantic_model": AzureShapeInfo(
        key="fabric_semantic_model",
        display_name="Fabric Semantic Model",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Semantic Model",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_kql_database": AzureShapeInfo(
        key="fabric_kql_database",
        display_name="Fabric KQL Database",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="KQL Database",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_sql_database": AzureShapeInfo(
        key="fabric_sql_database",
        display_name="Fabric SQL Database",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Fabric SQL Database",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_real_time_dashboard": AzureShapeInfo(
        key="fabric_real_time_dashboard",
        display_name="Fabric Real-Time Dashboard",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Real-Time Dashboard",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_data_agent": AzureShapeInfo(
        key="fabric_data_agent",
        display_name="Fabric Data Agent",
        category=AzureServiceCategory.AI_ML,
        stencil_name="Data Agent",
        stencil_file="FabricIcons",
        icon_color="#692B7C",
    ),
    "fabric_data_factory": AzureShapeInfo(
        key="fabric_data_factory",
        display_name="Fabric Data Factory",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Fabric Data Factory",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_model": AzureShapeInfo(
        key="fabric_model",
        display_name="Fabric ML Model",
        category=AzureServiceCategory.AI_ML,
        stencil_name="ML Model",
        stencil_file="FabricIcons",
        icon_color="#692B7C",
    ),
    "fabric_power_bi": AzureShapeInfo(
        key="fabric_power_bi",
        display_name="Power BI",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Power BI",
        stencil_file="FabricIcons",
        icon_color="#F2C811",
    ),
    "fabric_onelake": AzureShapeInfo(
        key="fabric_onelake",
        display_name="OneLake",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="OneLake",
        stencil_file="FabricIcons",
        icon_color="#008572",
    ),
    "fabric_purview": AzureShapeInfo(
        key="fabric_purview",
        display_name="Microsoft Purview",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Purview",
        stencil_file="FabricIcons",
        icon_color="#0078D4",
    ),
    "fabric_copilot": AzureShapeInfo(
        key="fabric_copilot",
        display_name="Fabric Copilot",
        category=AzureServiceCategory.AI_ML,
        stencil_name="Copilot",
        stencil_file="FabricIcons",
        icon_color="#692B7C",
    ),
    # ═══ New resource types (grounded from Azure GitHub org review) ═══
    # ── Networking – advanced ─────────────────────────────────────
    "route_table": AzureShapeInfo(
        key="route_table",
        display_name="Route Table",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Route Table",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Use UDRs to force traffic through Azure Firewall or NVAs for inspection.",
            "Reliability": "Avoid overly complex route tables that can cause black-holing.",
        },
    ),
    "private_link_service": AzureShapeInfo(
        key="private_link_service",
        display_name="Private Link Service",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Private Link Service",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Expose services privately to consumers across tenants/subscriptions.",
        },
    ),
    "ip_group": AzureShapeInfo(
        key="ip_group",
        display_name="IP Group",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="IP Groups",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "public_ip": AzureShapeInfo(
        key="public_ip",
        display_name="Public IP Address",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Public IP Addresses",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Minimize public IPs. Use DDoS Protection Standard. Prefer private endpoints.",
            "Cost Optimization": "Standard SKU Public IPs incur charges even when unassociated.",
        },
    ),
    "service_endpoint": AzureShapeInfo(
        key="service_endpoint",
        display_name="Service Endpoint Policy",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Service Endpoint Policies",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
    ),
    "firewall_policy": AzureShapeInfo(
        key="firewall_policy",
        display_name="Firewall Policy",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Firewall Policies",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Centralize firewall rules with Firewall Policy. Use rule collection groups for hierarchical policy.",
        },
    ),
    "application_security_group": AzureShapeInfo(
        key="application_security_group",
        display_name="Application Security Group",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Application Security Groups",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "Group VMs by workload for simplified NSG rule management.",
        },
    ),
    # ── Containers – advanced ─────────────────────────────────────
    "container_app_environment": AzureShapeInfo(
        key="container_app_environment",
        display_name="Container Apps Environment",
        category=AzureServiceCategory.CONTAINERS,
        stencil_name="Container Apps Environment",
        stencil_file="AzureContainers.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Deploy across Availability Zones. Use consumption+dedicated profiles for critical workloads.",
            "Security": "Use VNet injection and internal-only load balancer for private deployments.",
        },
    ),
    # ── Data & Analytics – advanced ───────────────────────────────
    "purview": AzureShapeInfo(
        key="purview",
        display_name="Microsoft Purview",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Azure Purview Accounts",
        stencil_file="AzureGovernance.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Operational Excellence": "Catalog and govern data assets. Automate data classification and lineage.",
            "Security": "Discover and classify sensitive data across the estate.",
        },
    ),
    "data_catalog": AzureShapeInfo(
        key="data_catalog",
        display_name="Data Catalog",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Data Catalog",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),
    "data_share": AzureShapeInfo(
        key="data_share",
        display_name="Azure Data Share",
        category=AzureServiceCategory.ANALYTICS,
        stencil_name="Data Share",
        stencil_file="AzureAnalytics.vssx",
        icon_color="#0078D4",
    ),
    # ── Integration – advanced ────────────────────────────────────
    "event_grid_domain": AzureShapeInfo(
        key="event_grid_domain",
        display_name="Event Grid Domain",
        category=AzureServiceCategory.INTEGRATION,
        stencil_name="Event Grid Domains",
        stencil_file="AzureIntegration.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Performance Efficiency": "Use domains for multi-tenant event architectures with thousands of topics.",
        },
    ),
    "event_grid_system_topic": AzureShapeInfo(
        key="event_grid_system_topic",
        display_name="Event Grid System Topic",
        category=AzureServiceCategory.INTEGRATION,
        stencil_name="Event Grid System Topics",
        stencil_file="AzureIntegration.vssx",
        icon_color="#0078D4",
    ),
    # ── Management & Governance – advanced ────────────────────────
    "blueprint": AzureShapeInfo(
        key="blueprint",
        display_name="Azure Blueprint",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Blueprints",
        stencil_file="AzureGovernance.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Operational Excellence": "Declaratively deploy sets of ARM templates, policies, and role assignments.",
        },
    ),
    "managed_grafana": AzureShapeInfo(
        key="managed_grafana",
        display_name="Azure Managed Grafana",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Azure Managed Grafana",
        stencil_file="AzureMonitor.vssx",
        icon_color="#F46800",
        waf_considerations={
            "Operational Excellence": "Visualize metrics from Azure Monitor, Prometheus, and other sources.",
        },
    ),
    "action_group": AzureShapeInfo(
        key="action_group",
        display_name="Action Group",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Action Groups",
        stencil_file="AzureMonitor.vssx",
        icon_color="#0078D4",
    ),
    "alert_rule": AzureShapeInfo(
        key="alert_rule",
        display_name="Alert Rule",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Alerts",
        stencil_file="AzureMonitor.vssx",
        icon_color="#0078D4",
    ),
    "diagnostic_setting": AzureShapeInfo(
        key="diagnostic_setting",
        display_name="Diagnostic Setting",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Diagnostic Settings",
        stencil_file="AzureMonitor.vssx",
        icon_color="#0078D4",
    ),
    # ── Security – advanced ───────────────────────────────────────
    "application_gateway_waf_v2": AzureShapeInfo(
        key="application_gateway_waf_v2",
        display_name="Application Gateway WAF v2",
        category=AzureServiceCategory.NETWORKING,
        stencil_name="Application Gateways",
        stencil_file="AzureNetworking.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Security": "WAF v2 with OWASP 3.2 rule sets. Use Prevention mode in production.",
            "Reliability": "Zone-redundant by default. Configure health probes.",
            "Performance Efficiency": "Autoscale instance count based on traffic.",
        },
    ),
    # ── DevOps – advanced ─────────────────────────────────────────
    "github_actions": AzureShapeInfo(
        key="github_actions",
        display_name="GitHub Actions",
        category=AzureServiceCategory.DEVOPS,
        stencil_name="GitHub Actions",
        stencil_file="AzureDevOps.vssx",
        icon_color="#2088FF",
        waf_considerations={
            "Operational Excellence": "Use OIDC federated credentials for keyless deployment to Azure.",
        },
    ),
    "load_testing": AzureShapeInfo(
        key="load_testing",
        display_name="Azure Load Testing",
        category=AzureServiceCategory.DEVOPS,
        stencil_name="Azure Load Testing",
        stencil_file="AzureDevOps.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Performance Efficiency": "Run JMeter-based load tests. Integrate into CI/CD for regression.",
        },
    ),
    # ── IoT – advanced ────────────────────────────────────────────
    "iot_edge": AzureShapeInfo(
        key="iot_edge",
        display_name="Azure IoT Edge",
        category=AzureServiceCategory.IOT,
        stencil_name="Azure IoT Edge",
        stencil_file="AzureIoT.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Deploy modules to edge devices for offline capability.",
            "Performance Efficiency": "Process data at the edge to reduce cloud bandwidth.",
        },
    ),
    "digital_twins": AzureShapeInfo(
        key="digital_twins",
        display_name="Azure Digital Twins",
        category=AzureServiceCategory.IOT,
        stencil_name="Digital Twins",
        stencil_file="AzureIoT.vssx",
        icon_color="#0078D4",
    ),
    "time_series_insights": AzureShapeInfo(
        key="time_series_insights",
        display_name="Time Series Insights",
        category=AzureServiceCategory.IOT,
        stencil_name="Time Series Insights",
        stencil_file="AzureIoT.vssx",
        icon_color="#0078D4",
    ),
    # ── Migration ─────────────────────────────────────────────────
    "migrate": AzureShapeInfo(
        key="migrate",
        display_name="Azure Migrate",
        category=AzureServiceCategory.MIGRATION,
        stencil_name="Azure Migrate",
        stencil_file="AzureMigrate.vssx",
        icon_color="#0078D4",
    ),
    "database_migration_service": AzureShapeInfo(
        key="database_migration_service",
        display_name="Database Migration Service",
        category=AzureServiceCategory.DATABASES,
        stencil_name="Database Migration Service",
        stencil_file="AzureDatabases.vssx",
        icon_color="#0078D4",
    ),
    # ── Health / Specialized ──────────────────────────────────────
    "api_for_fhir": AzureShapeInfo(
        key="api_for_fhir",
        display_name="Azure API for FHIR",
        category=AzureServiceCategory.INTEGRATION,
        stencil_name="Azure API for FHIR",
        stencil_file="AzureIntegration.vssx",
        icon_color="#0078D4",
    ),
    "chaos_studio": AzureShapeInfo(
        key="chaos_studio",
        display_name="Azure Chaos Studio",
        category=AzureServiceCategory.MANAGEMENT,
        stencil_name="Chaos Studio",
        stencil_file="AzureGovernance.vssx",
        icon_color="#0078D4",
        waf_considerations={
            "Reliability": "Run chaos experiments to validate fault tolerance before production.",
        },
    ),
}


# ── Boundary style definitions ────────────────────────────────────
BOUNDARY_STYLES: dict[str, dict] = {
    "subscription": {
        "fill_color": "#E8F0FE",
        "line_color": "#4285F4",
        "line_weight": 2,
        "corner_radius": 0.15,
        "label_position": "top-left",
    },
    "resource_group": {
        "fill_color": "#F0F0F0",
        "line_color": "#808080",
        "line_weight": 1.5,
        "corner_radius": 0.1,
        "line_pattern": "dashed",
        "label_position": "top-left",
    },
    "vnet": {
        "fill_color": "#E6F3FF",
        "line_color": "#0078D4",
        "line_weight": 1.5,
        "corner_radius": 0.1,
        "label_position": "top-left",
    },
    "subnet": {
        "fill_color": "#F0F8FF",
        "line_color": "#5B9BD5",
        "line_weight": 1,
        "corner_radius": 0.05,
        "line_pattern": "dashed",
        "label_position": "top-left",
    },
    "availability_zone": {
        "fill_color": "#FFF8E1",
        "line_color": "#FFA000",
        "line_weight": 1,
        "corner_radius": 0.1,
        "line_pattern": "dashed",
        "label_position": "top-right",
    },
    "region": {
        "fill_color": "#FAFAFA",
        "line_color": "#333333",
        "line_weight": 2,
        "corner_radius": 0.2,
        "label_position": "top-center",
    },
    "management_group": {
        "fill_color": "#F3E5F5",
        "line_color": "#7B1FA2",
        "line_weight": 2,
        "corner_radius": 0.15,
        "label_position": "top-left",
    },
    "nsg": {
        "fill_color": "#FFEBEE",
        "line_color": "#D32F2F",
        "line_weight": 1,
        "corner_radius": 0.05,
        "line_pattern": "dotted",
        "label_position": "top-right",
    },
}


# ── Connector style definitions ───────────────────────────────────
CONNECTOR_STYLES: dict[str, dict] = {
    "data_flow": {"color": "#0078D4", "weight": 1.5, "pattern": "solid", "arrow": "end"},
    "network": {"color": "#333333", "weight": 1.0, "pattern": "solid", "arrow": "both"},
    "dependency": {"color": "#808080", "weight": 1.0, "pattern": "dashed", "arrow": "end"},
    "reference": {"color": "#B0B0B0", "weight": 0.75, "pattern": "dotted", "arrow": "none"},
    "vpn_tunnel": {"color": "#FFA000", "weight": 2.0, "pattern": "dashed", "arrow": "both"},
    "expressroute": {"color": "#7B1FA2", "weight": 2.5, "pattern": "solid", "arrow": "both"},
}


def get_shape(key: str) -> AzureShapeInfo | None:
    """Look up an Azure shape by key (resolves aliases)."""
    return AZURE_SHAPE_CATALOG.get(resolve_alias(key))


def search_shapes(query: str, category: str | None = None) -> list[AzureShapeInfo]:
    """Search shapes by name, category, or alias."""
    query_lower = query.lower()

    # If the query matches an alias exactly, include the target
    alias_target = RESOURCE_ALIASES.get(query_lower)

    results = []
    seen = set()
    for shape in AZURE_SHAPE_CATALOG.values():
        if category and shape.category.value.lower() != category.lower():
            continue
        if (
            query_lower in shape.key.lower()
            or query_lower in shape.display_name.lower()
            or query_lower in shape.category.value.lower()
            or shape.key == alias_target
        ):
            if shape.key not in seen:
                results.append(shape)
                seen.add(shape.key)
    return results


def list_categories() -> list[str]:
    """List all available Azure service categories."""
    return sorted(set(s.category.value for s in AZURE_SHAPE_CATALOG.values()))


def resolve_svg_path(key: str, icons_root: str | Path | None = None) -> Path | None:
    """Resolve the full filesystem path to an SVG icon for a resource type.

    Args:
        key: Resource type key (e.g., 'virtual_machine').
        icons_root: Root directory containing the icon category folders.
                    Defaults to the bundled stencils directory.

    Returns:
        Absolute path to the SVG file, or None if not found.
    """
    root = Path(icons_root) if icons_root else _DEFAULT_ICONS_ROOT
    relative = SVG_ICON_MAP.get(key)
    if not relative:
        return None
    full_path = root / relative
    return full_path if full_path.exists() else None


def get_icons_root() -> Path:
    """Return the default icons root directory."""
    return _DEFAULT_ICONS_ROOT


# ── Auto-populate svg_icon field from SVG_ICON_MAP ────────────────
for _key, _svg_path in SVG_ICON_MAP.items():
    if _key in AZURE_SHAPE_CATALOG:
        AZURE_SHAPE_CATALOG[_key].svg_icon = _svg_path
