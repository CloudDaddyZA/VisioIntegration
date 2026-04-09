"""Data models for the Visio Azure MCP server."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AzureServiceCategory(str, Enum):
    COMPUTE = "Compute"
    NETWORKING = "Networking"
    STORAGE = "Storage"
    DATABASES = "Databases"
    SECURITY = "Security"
    IDENTITY = "Identity"
    INTEGRATION = "Integration"
    ANALYTICS = "Analytics"
    AI_ML = "AI + Machine Learning"
    DEVOPS = "DevOps"
    MANAGEMENT = "Management + Governance"
    WEB = "Web"
    CONTAINERS = "Containers"
    IOT = "IoT"
    MESSAGING = "Messaging"
    MIGRATION = "Migration"
    MIXED_REALITY = "Mixed Reality"
    MEDIA = "Media"
    GENERAL = "General"


class WafPillar(str, Enum):
    RELIABILITY = "Reliability"
    SECURITY = "Security"
    COST_OPTIMIZATION = "Cost Optimization"
    OPERATIONAL_EXCELLENCE = "Operational Excellence"
    PERFORMANCE_EFFICIENCY = "Performance Efficiency"


class CafPrinciple(str, Enum):
    NAMING = "Naming Convention"
    RESOURCE_ORGANIZATION = "Resource Organization"
    NETWORK_TOPOLOGY = "Network Topology"
    IDENTITY = "Identity and Access"
    GOVERNANCE = "Governance"
    SECURITY_BASELINE = "Security Baseline"
    MANAGEMENT = "Management and Monitoring"


class Position(BaseModel):
    x: float = Field(description="X coordinate in inches from left")
    y: float = Field(description="Y coordinate in inches from top")


class Size(BaseModel):
    width: float = Field(default=1.0, description="Width in inches")
    height: float = Field(default=1.0, description="Height in inches")


class DiagramResource(BaseModel):
    """Represents an Azure resource placed on the diagram."""
    id: str = Field(description="Unique identifier for this resource instance")
    resource_type: str = Field(description="Azure resource type key (e.g., 'virtual_machine', 'app_service')")
    display_name: str = Field(description="Display label for the resource")
    position: Position = Field(default_factory=lambda: Position(x=4.0, y=4.0))
    size: Size = Field(default_factory=Size)
    properties: dict = Field(default_factory=dict, description="Additional properties (SKU, tier, region, etc.)")
    group_id: Optional[str] = Field(default=None, description="ID of the boundary group this belongs to")


class Connection(BaseModel):
    """Represents a connection between two resources."""
    id: str = Field(description="Unique identifier for this connection")
    source_id: str = Field(description="ID of the source resource")
    target_id: str = Field(description="ID of the target resource")
    label: str = Field(default="", description="Label on the connector")
    connection_type: str = Field(default="data_flow", description="Type: data_flow, network, dependency, reference")
    style: str = Field(default="solid", description="Line style: solid, dashed, dotted")


class BoundaryGroup(BaseModel):
    """Represents a visual boundary/container (resource group, VNet, subnet, etc.)."""
    id: str = Field(description="Unique identifier for this boundary")
    boundary_type: str = Field(description="Type: subscription, resource_group, vnet, subnet, availability_zone, region, management_group, nsg")
    display_name: str = Field(description="Display label")
    position: Position = Field(default_factory=lambda: Position(x=1.0, y=1.0))
    size: Size = Field(default_factory=lambda: Size(width=6.0, height=4.0))
    parent_id: Optional[str] = Field(default=None, description="ID of parent boundary for nesting")
    properties: dict = Field(default_factory=dict)


class DiagramState(BaseModel):
    """Complete state of the current diagram."""
    name: str = Field(default="Azure Architecture", description="Diagram title")
    resources: dict[str, DiagramResource] = Field(default_factory=dict)
    connections: dict[str, Connection] = Field(default_factory=dict)
    boundaries: dict[str, BoundaryGroup] = Field(default_factory=dict)
    page_width: float = Field(default=22.0, description="Page width in inches")
    page_height: float = Field(default=17.0, description="Page height in inches")
    # Layout hints from reference architectures (preserved for re-layout)
    _layout_hints: dict[str, tuple[float, float]] = {}
    _boundary_hints: dict[str, tuple[float, float, float, float]] = {}

    model_config = {"arbitrary_types_allowed": True}


class ValidationFinding(BaseModel):
    """A single WAF or CAF validation finding."""
    severity: str = Field(description="critical, warning, or info")
    pillar: str = Field(description="WAF pillar or CAF principle")
    message: str = Field(description="Description of the finding")
    recommendation: str = Field(description="Recommended action")
    affected_resources: list[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    """Complete validation report."""
    framework: str = Field(description="WAF or CAF")
    score: float = Field(description="Overall score 0-100")
    findings: list[ValidationFinding] = Field(default_factory=list)
    summary: str = Field(default="")


class AzureShapeInfo(BaseModel):
    """Metadata about an available Azure shape."""
    key: str = Field(description="Unique key for this resource type")
    display_name: str = Field(description="Human-readable name")
    category: AzureServiceCategory
    stencil_name: str = Field(description="Visio stencil master name")
    stencil_file: str = Field(description="Visio stencil file (.vssx)")
    svg_icon: str = Field(default="", description="Relative path to SVG icon file from icons root")
    icon_color: str = Field(default="#0078D4", description="Primary icon color hex")
    waf_considerations: dict[str, str] = Field(default_factory=dict, description="WAF pillar tips for this resource")
