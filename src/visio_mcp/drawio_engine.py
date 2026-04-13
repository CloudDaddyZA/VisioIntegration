"""Draw.io (mxGraph XML) rendering engine for Azure architecture diagrams.

Converts a DiagramState into a .drawio file that can be opened in
draw.io desktop, the VS Code draw.io extension, or diagrams.net.

Uses plain (uncompressed) mxGraph XML for readability and diffability.
Azure resources are rendered with draw.io's built-in Azure icon shapes
where available, falling back to labeled rounded rectangles.
"""

from __future__ import annotations

import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from .azure_catalog import BOUNDARY_STYLES, CONNECTOR_STYLES
from .models import BoundaryGroup, Connection, DiagramResource, DiagramState

logger = logging.getLogger(__name__)

# ── Pixels-per-inch conversion ────────────────────────────────────
# DiagramState uses inches; draw.io uses pixels (approx 96 px/in).
PPI = 96


def _in2px(inches: float) -> float:
    return round(inches * PPI, 1)


# ── Azure shape → draw.io style mapping ──────────────────────────
# draw.io includes built-in Azure 2021 shapes via the "mxgraph.azure" shape library.
# Keys here mirror azure_catalog resource_type keys.
# Style strings reference shapes from the mxgraph.azure stencil set.
DRAWIO_AZURE_STYLES: dict[str, str] = {
    # Compute
    "virtual_machine": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/compute/Virtual_Machine.svg;",
    "vm_scale_set": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/compute/VM_Scale_Sets.svg;",
    "app_service": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/app_services/App_Services.svg;",
    "app_service_plan": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/app_services/App_Service_Plans.svg;",
    "function_app": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/compute/Function_Apps.svg;",
    "container_instances": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/compute/Container_Instances.svg;",
    "container_apps": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/compute/Container_Instances.svg;",
    "kubernetes_service": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/containers/Kubernetes_Services.svg;",
    "container_registry": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/containers/Container_Registries.svg;",
    "service_fabric": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/containers/Service_Fabric_Clusters.svg;",
    "batch_account": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/compute/Batch_Accounts.svg;",
    "spring_apps": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/compute/Azure_Spring_Cloud.svg;",
    # Networking
    "virtual_network": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Virtual_Networks.svg;",
    "subnet": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Subnet.svg;",
    "load_balancer": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Load_Balancers.svg;",
    "application_gateway": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Application_Gateways.svg;",
    "front_door": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Front_Doors.svg;",
    "traffic_manager": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Traffic_Manager_Profiles.svg;",
    "dns_zone": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/DNS_Zones.svg;",
    "private_endpoint": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Private_Endpoint.svg;",
    "private_link": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Private_Link_Service.svg;",
    "vpn_gateway": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Virtual_Network_Gateways.svg;",
    "expressroute": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/ExpressRoute_Circuits.svg;",
    "firewall": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Firewalls.svg;",
    "nsg": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Network_Security_Groups.svg;",
    "bastion": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Bastions.svg;",
    "ddos_protection": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/DDoS_Protection_Plans.svg;",
    "nat_gateway": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/NAT.svg;",
    "cdn_profile": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/CDN_Profiles.svg;",
    "network_watcher": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Network_Watcher.svg;",
    "virtual_wan": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Virtual_WANs.svg;",
    "web_app_firewall": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/Web_Application_Firewall_Policies_WAF.svg;",
    # Storage
    "storage_account": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/storage/Storage_Accounts.svg;",
    "blob_storage": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/general/Blob_Block.svg;",
    "data_lake_storage": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/storage/Data_Lake_Storage_Gen1.svg;",
    "managed_disk": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/compute/Disks.svg;",
    "file_share": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/storage/Azure_Fileshare.svg;",
    "netapp_files": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/storage/Azure_NetApp_Files.svg;",
    # Databases
    "sql_database": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/SQL_Database.svg;",
    "sql_managed_instance": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/SQL_Managed_Instance.svg;",
    "azure_sql": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/Azure_SQL.svg;",
    "azure_sql_vm": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/Azure_SQL_VM.svg;",
    "sql_elastic_pool": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/SQL_Elastic_Pools.svg;",
    "cosmos_db": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/Azure_Cosmos_DB.svg;",
    "mysql_database": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/Azure_Database_MySQL_Server.svg;",
    "postgresql_database": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/Azure_Database_PostgreSQL_Server.svg;",
    "mariadb_database": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/Azure_Database_MariaDB_Server.svg;",
    "redis_cache": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/databases/Cache_Redis.svg;",
    # Security
    "key_vault": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/security/Key_Vaults.svg;",
    "defender_for_cloud": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/security/Security_Center.svg;",
    "sentinel": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/security/Azure_Sentinel.svg;",
    # Identity
    "managed_identity": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/identity/Managed_Identities.svg;",
    "entra_id": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/identity/Azure_Active_Directory.svg;",
    "app_registration": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/identity/App_Registrations.svg;",
    "user": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/identity/Users.svg;",
    # Integration
    "api_management": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/integration/API_Management_Services.svg;",
    "logic_app": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/integration/Logic_Apps.svg;",
    "service_bus": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/integration/Service_Bus.svg;",
    "event_grid": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/integration/Event_Grid_Topics.svg;",
    # Analytics
    "event_hub": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/analytics/Event_Hubs.svg;",
    "synapse_analytics": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/analytics/Azure_Synapse_Analytics.svg;",
    "data_factory": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/analytics/Data_Factory.svg;",
    "databricks": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/analytics/Azure_Databricks.svg;",
    "stream_analytics": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/analytics/Stream_Analytics_Jobs.svg;",
    "data_explorer": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/analytics/Azure_Data_Explorer_Clusters.svg;",
    "hdinsight": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/analytics/HD_Insight_Clusters.svg;",
    # AI + ML
    "openai_service": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/ai_machine_learning/Azure_OpenAI.svg;",
    "cognitive_services": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/ai_machine_learning/Cognitive_Services.svg;",
    "machine_learning": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/ai_machine_learning/Machine_Learning.svg;",
    "ai_search": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/app_services/Search_Services.svg;",
    "bot_service": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/ai_machine_learning/Bot_Services.svg;",
    # Monitor / Management
    "monitor": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Monitor.svg;",
    "log_analytics": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Log_Analytics_Workspaces.svg;",
    "application_insights": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Application_Insights.svg;",
    "policy": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Policy.svg;",
    "automation_account": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Automation_Accounts.svg;",
    "azure_arc": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Azure_Arc.svg;",
    "advisor": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Advisor.svg;",
    "cost_management": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Cost_Management_and_Billing.svg;",
    "recovery_services_vault": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/management_governance/Recovery_Services_Vaults.svg;",
    # General
    "resource_group": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/general/Resource_Groups.svg;",
    "subscription": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/general/Subscriptions.svg;",
    "management_group": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/general/Management_Groups.svg;",
    # DevOps / IoT / Web / Other
    "devops": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/devops/Azure_DevOps.svg;",
    "iot_hub": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/iot/IoT_Hub.svg;",
    "iot_central": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/iot/IoT_Central_Applications.svg;",
    "static_web_app": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/app_services/App_Services.svg;",
    "signalr": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/web/SignalR.svg;",
    "on_premises": "aspect=fixed;html=1;perimeter=none;image;image=img/lib/azure2/networking/On_Premises_Data_Gateways.svg;",
    "internet": "shape=mxgraph.azure.cloud;fillColor=#0078D4;fontColor=#FFFFFF;strokeColor=none;",
}

# Fallback style for unknown resource types
_FALLBACK_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;arcSize=10;"
    "fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;"
)


def _hex_to_drawio(hex_color: str) -> str:
    """Ensure a hex color has a '#' prefix for draw.io style strings."""
    if hex_color and not hex_color.startswith("#"):
        return f"#{hex_color}"
    return hex_color


class DrawioEngine:
    """Renders a DiagramState into a .drawio (mxGraph XML) file."""

    def __init__(self) -> None:
        self._cell_id = 2  # 0 and 1 are reserved by mxGraph root cells
        # Absolute positions of boundaries (inches) for coordinate conversion.
        # draw.io uses parent-relative coordinates, so children must subtract
        # their parent's absolute position.
        self._boundary_abs_pos: dict[str, tuple[float, float]] = {}

    def _next_id(self) -> str:
        cid = str(self._cell_id)
        self._cell_id += 1
        return cid

    def _get_parent_offset(self, parent_id: str | None) -> tuple[float, float]:
        """Return the absolute position (inches) of a parent boundary, or (0,0) for root."""
        if parent_id and parent_id in self._boundary_abs_pos:
            return self._boundary_abs_pos[parent_id]
        return (0.0, 0.0)

    # ── Public API ────────────────────────────────────────────────

    def render(self, state: DiagramState, output_path: str) -> str:
        """Render the diagram state to a .drawio file. Returns the output path."""
        output_path = os.path.abspath(output_path)

        # Build XML tree
        mxfile = ET.Element("mxfile", host="Copilot", type="device")
        diagram = ET.SubElement(mxfile, "diagram", name=state.name, id="page-1")
        model = ET.SubElement(
            diagram, "mxGraphModel",
            dx="0", dy="0", grid="1", gridSize="10",
            guides="1", tooltips="1", connect="1",
            arrows="1", fold="1",
            pageWidth=str(int(_in2px(state.page_width))),
            pageHeight=str(int(_in2px(state.page_height))),
            math="0", shadow="0",
        )
        root = ET.SubElement(model, "root")

        # Required root cells (layer 0 and default parent)
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")

        # Track resource_id → mxCell id for connections
        id_map: dict[str, str] = {}

        # Pre-compute absolute positions for all boundaries so children
        # can calculate parent-relative coordinates.
        for b in state.boundaries.values():
            self._boundary_abs_pos[b.id] = (b.position.x, b.position.y)

        # ── Boundaries ────────────────────────────────────────────
        # Sort by area descending so larger containers come first
        sorted_boundaries = sorted(
            state.boundaries.values(),
            key=lambda b: b.size.width * b.size.height,
            reverse=True,
        )
        for boundary in sorted_boundaries:
            cell_id = self._next_id()
            id_map[boundary.id] = cell_id
            self._add_boundary(root, boundary, cell_id, id_map)

        # ── Resources ─────────────────────────────────────────────
        for resource in state.resources.values():
            cell_id = self._next_id()
            id_map[resource.id] = cell_id
            # Label goes below the icon
            label_id = self._next_id()
            self._add_resource(root, resource, cell_id, label_id, id_map)

        # ── Connections ───────────────────────────────────────────
        for connection in state.connections.values():
            cell_id = self._next_id()
            self._add_connection(root, connection, cell_id, id_map)

        # ── Title ─────────────────────────────────────────────────
        title_id = self._next_id()
        self._add_title(root, state.name, title_id)

        # Write file
        tree = ET.ElementTree(mxfile)
        ET.indent(tree, space="  ")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        tree.write(output_path, encoding="UTF-8", xml_declaration=True)

        logger.info("Diagram saved to %s (draw.io)", output_path)
        return output_path

    # ── Internal helpers ──────────────────────────────────────────

    def _add_boundary(
        self, root: ET.Element, boundary: BoundaryGroup,
        cell_id: str, id_map: dict[str, str],
    ) -> None:
        """Add a boundary group as a styled rectangle with a label."""
        bstyle = BOUNDARY_STYLES.get(boundary.boundary_type, BOUNDARY_STYLES.get("resource_group", {}))
        fill = _hex_to_drawio(bstyle.get("fill_color", "#F0F0F0"))
        stroke = _hex_to_drawio(bstyle.get("line_color", "#808080"))
        weight = bstyle.get("line_weight", 1.5)
        pattern = bstyle.get("line_pattern", "solid")
        radius = bstyle.get("corner_radius", 0.1)

        # Build style string
        parts = [
            "rounded=1", "whiteSpace=wrap", "html=1",
            f"arcSize={int(radius * 100)}",
            f"fillColor={fill}", "fillOpacity=40",
            f"strokeColor={stroke}", f"strokeWidth={weight}",
            "verticalAlign=top", "align=left", "spacingLeft=8", "spacingTop=4",
            "fontSize=12", "fontStyle=1",
            "container=1", "collapsible=0",
        ]
        if pattern == "dashed":
            parts.append("dashed=1;dashPattern=8 4")
        elif pattern == "dotted":
            parts.append("dashed=1;dashPattern=2 2")

        style = ";".join(parts) + ";"

        # Parent cell: nest inside parent boundary if specified
        parent = id_map.get(boundary.parent_id, "1") if boundary.parent_id else "1"

        # Convert to parent-relative coordinates
        off_x, off_y = self._get_parent_offset(boundary.parent_id)
        rel_x = boundary.position.x - off_x
        rel_y = boundary.position.y - off_y

        cell = ET.SubElement(root, "mxCell", id=cell_id, value=boundary.display_name,
                             style=style, vertex="1", parent=parent)
        ET.SubElement(cell, "mxGeometry",
                      x=str(_in2px(rel_x)),
                      y=str(_in2px(rel_y)),
                      width=str(_in2px(boundary.size.width)),
                      height=str(_in2px(boundary.size.height)),
                      **{"as": "geometry"})

    def _add_resource(
        self, root: ET.Element, resource: DiagramResource,
        cell_id: str, label_id: str, id_map: dict[str, str],
    ) -> None:
        """Add a resource as an Azure icon shape plus a text label below."""
        style = DRAWIO_AZURE_STYLES.get(resource.resource_type, _FALLBACK_STYLE)
        is_icon = resource.resource_type in DRAWIO_AZURE_STYLES

        # Parent cell: if resource belongs to a boundary group
        parent = id_map.get(resource.group_id, "1") if resource.group_id else "1"

        # Convert to parent-relative coordinates
        off_x, off_y = self._get_parent_offset(resource.group_id)
        rel_x = resource.position.x - off_x
        rel_y = resource.position.y - off_y

        icon_w = _in2px(0.6)
        icon_h = _in2px(0.6)

        if is_icon:
            # Icon cell (no label — label is separate below)
            cell = ET.SubElement(root, "mxCell", id=cell_id, value="",
                                 style=style, vertex="1", parent=parent)
            ET.SubElement(cell, "mxGeometry",
                          x=str(_in2px(rel_x)),
                          y=str(_in2px(rel_y)),
                          width=str(icon_w), height=str(icon_h),
                          **{"as": "geometry"})

            # Label cell below the icon
            label_style = (
                "text;html=1;align=center;verticalAlign=top;"
                "resizable=0;points=[];autosize=1;"
                "strokeColor=none;fillColor=none;fontSize=10;"
            )
            label_cell = ET.SubElement(root, "mxCell", id=label_id,
                                       value=resource.display_name,
                                       style=label_style, vertex="1", parent=parent)
            label_w = max(_in2px(1.2), len(resource.display_name) * 6.5)
            label_x = _in2px(rel_x) + icon_w / 2 - label_w / 2
            label_y = _in2px(rel_y) + icon_h + 4
            ET.SubElement(label_cell, "mxGeometry",
                          x=str(round(label_x, 1)),
                          y=str(round(label_y, 1)),
                          width=str(round(label_w, 1)), height=str(_in2px(0.25)),
                          **{"as": "geometry"})
        else:
            # Fallback: single labeled rectangle
            cell = ET.SubElement(root, "mxCell", id=cell_id,
                                 value=resource.display_name,
                                 style=style, vertex="1", parent=parent)
            ET.SubElement(cell, "mxGeometry",
                          x=str(_in2px(rel_x)),
                          y=str(_in2px(rel_y)),
                          width=str(_in2px(resource.size.width)),
                          height=str(_in2px(resource.size.height)),
                          **{"as": "geometry"})

    def _add_connection(
        self, root: ET.Element, connection: Connection,
        cell_id: str, id_map: dict[str, str],
    ) -> None:
        """Add a connection as an edge between two resource cells."""
        source_cell = id_map.get(connection.source_id)
        target_cell = id_map.get(connection.target_id)
        if not source_cell or not target_cell:
            logger.warning(
                "Skipping connection %s: missing source/target cell", connection.id
            )
            return

        cstyle = CONNECTOR_STYLES.get(connection.connection_type, CONNECTOR_STYLES.get("data_flow", {}))
        color = _hex_to_drawio(cstyle.get("color", "#0078D4"))
        weight = cstyle.get("weight", 1.5)
        pattern = cstyle.get("pattern", "solid")
        arrow = cstyle.get("arrow", "end")

        parts = [
            "edgeStyle=orthogonalEdgeStyle",
            "rounded=1",
            "html=1",
            f"strokeColor={color}",
            f"strokeWidth={weight}",
            "fontSize=10",
            "exitX=0.5;exitY=1;exitDx=0;exitDy=0",
        ]

        # Arrow direction
        if arrow == "none":
            parts.append("endArrow=none")
        elif arrow == "both":
            parts.append("startArrow=classic;endArrow=classic")
        else:
            parts.append("endArrow=classic;startArrow=none")

        # Dash pattern
        if pattern == "dashed":
            parts.append("dashed=1;dashPattern=8 4")
        elif pattern == "dotted":
            parts.append("dashed=1;dashPattern=2 2")

        style = ";".join(parts) + ";"

        cell = ET.SubElement(root, "mxCell", id=cell_id,
                             value=connection.label,
                             style=style, edge="1",
                             source=source_cell, target=target_cell,
                             parent="1")
        ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})

    def _add_title(self, root: ET.Element, title: str, cell_id: str) -> None:
        """Add a title label at the top of the diagram."""
        style = (
            "text;html=1;align=center;verticalAlign=middle;"
            "resizable=0;points=[];autosize=1;"
            "strokeColor=none;fillColor=none;"
            "fontSize=18;fontStyle=1;fontColor=#333333;"
        )
        cell = ET.SubElement(root, "mxCell", id=cell_id, value=title,
                             style=style, vertex="1", parent="1")
        title_w = max(300, len(title) * 12)
        ET.SubElement(cell, "mxGeometry",
                      x=str(_in2px(1.0)), y=str(_in2px(0.3)),
                      width=str(title_w), height=str(40),
                      **{"as": "geometry"})
