"""Azure Architecture Center reference architecture templates.

Based on official Microsoft reference architectures from:
  https://learn.microsoft.com/en-us/azure/architecture/

Each template defines the standard resources, connections, boundaries,
and workflow numbering that Microsoft uses in their published diagrams.

Visual standards follow:
  https://learn.microsoft.com/en-us/azure/architecture/icons/
  https://learn.microsoft.com/en-us/azure/well-architected/architect-role/design-diagrams

Diagram conventions enforced:
  - Use official Azure icons at 1:1 aspect ratio (no crop/flip/rotate)
  - Include product name label adjacent to every icon
  - Top-to-bottom or left-to-right traffic flow
  - Numbered workflow steps (circled) on data-flow arrows
  - Group resources inside VNet/subnet/RG boundaries
  - Show private endpoints explicitly as separate shapes
  - Use dashed lines for management/identity flows
  - Use solid lines for data flows
  - Gray background for boundaries/grouping boxes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── Microsoft official color palette for architecture diagrams ────
# Source: Azure Architecture Center SVG diagrams + icon set
AZURE_DIAGRAM_COLORS = {
    # Primary Azure brand
    "azure_blue": "#0078D4",
    "azure_dark_blue": "#003067",
    "azure_light_blue": "#50E6FF",

    # Resource category colors (as used in Architecture Center SVGs)
    "compute": "#0078D4",
    "networking": "#0078D4",
    "storage": "#0078D4",
    "databases": "#0078D4",
    "security": "#E74856",
    "identity": "#FFB900",
    "ai_ml": "#692B7C",
    "analytics": "#008572",
    "integration": "#005BA1",
    "iot": "#008272",
    "devops": "#F25022",
    "management": "#107C10",

    # Boundary/grouping colors — actual MS Architecture Center SVGs use
    # nearly all gray/white fills, NOT colored per boundary type.
    # CSS classes st2/st3: #FFFFFF, st4/st91: #F2F2F2, st6: #F8F8F8
    "boundary_subscription": "#FFFFFF",
    "boundary_resource_group": "#F2F2F2",
    "boundary_vnet": "#FFFFFF",
    "boundary_subnet": "#F2F2F2",
    "boundary_security_zone": "#F2F2F2",
    "boundary_management_group": "#F8F8F8",
    "boundary_region": "#F8F8F8",

    # Connector colors — MS Architecture Center uses BLACK for ALL connectors
    # (CSS classes st11, st46, st49: stroke:#000000)
    "data_flow": "#000000",
    "management_flow": "#000000",
    "identity_flow": "#000000",
    "network_flow": "#000000",
    "private_link": "#000000",

    # Text — MS uses black (#000000) for labels, Segoe UI font
    "label_primary": "#000000",
    "label_secondary": "#000000",
    # Step number circles: GREEN (#107C10) with white text (CSS st96/st97)
    "step_number_bg": "#107C10",
    "step_number_fg": "#FFFFFF",
    # Boundary labels: blue-gray per MS (CSS st10: #5B9BD5)
    "boundary_label": "#5B9BD5",
}


# ── Microsoft diagram layout standards ───────────────────────────

@dataclass
class DiagramStandards:
    """Layout and visual standards per Azure Architecture Center."""

    # Icon sizing (inches) - per Microsoft guidelines
    resource_icon_size: float = 0.6          # Service icons at 0.6"
    resource_with_label_height: float = 1.2  # Icon + label below
    resource_h_spacing: float = 1.8          # Horizontal gap between resources
    resource_v_spacing: float = 2.0          # Vertical gap between tiers

    # Boundary styling — per actual MS Architecture Center SVG CSS
    # st2: stroke-width:0.5, st4: stroke-width:1
    boundary_corner_radius: float = 0.0      # MS diagrams use sharp corners
    boundary_padding: float = 0.8
    boundary_header_height: float = 0.5
    boundary_stroke_width: float = 0.5       # pt — MS uses 0.5pt (st2)
    boundary_stroke_dash: str = "3.5 2.5"    # MS dasharray: 3.5,2.5

    # Connector styling — MS uses 1pt black connectors
    connector_width: float = 1.0             # pt (st11: stroke-width:1)
    connector_arrow_size: float = 0.15       # inches
    step_number_radius: float = 0.18         # Workflow step circle radius

    # Page layout
    page_margin: float = 1.0
    title_font_size: float = 16.0            # pt
    subtitle_font_size: float = 12.0
    label_font_size: float = 9.0             # ~0.833em of 12pt base
    boundary_label_font_size: float = 9.0    # MS: 0.833em

    # Font family — MS Architecture Center uses Segoe UI
    font_family: str = "Segoe UI"

    # Flow direction: "TB" (top-bottom) or "LR" (left-right)
    flow_direction: str = "TB"


# Default standards instance
MICROSOFT_STANDARDS = DiagramStandards()


# ── Azure Architecture Styles ────────────────────────────────────
# Source: https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/
#
# These are the standard architecture patterns identified by Microsoft.
# Each style defines typical components, layout conventions, and
# recommended Azure services for diagramming.

@dataclass
class ArchitectureStyle:
    """An Azure Architecture Center architecture style/pattern."""
    key: str
    name: str
    description: str
    source_url: str
    when_to_use: list[str]
    typical_components: list[str]
    azure_services: list[str]
    flow_direction: str                 # TB or LR
    layout_strategy: str                # tiered, grouped, etc.
    diagram_conventions: list[str]      # How to draw this style


ARCHITECTURE_STYLES: dict[str, ArchitectureStyle] = {
    "n_tier": ArchitectureStyle(
        key="n_tier",
        name="N-Tier",
        description=(
            "Traditional layered architecture dividing an application into "
            "presentation, business logic, and data tiers. Each tier runs on "
            "separate infrastructure separated by subnets. Supports closed-layer "
            "(strict adjacent-tier calls) or open-layer (skip tiers) models."
        ),
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/n-tier",
        when_to_use=[
            "Migrating on-premises layered applications to Azure",
            "Applications with low update frequency",
            "Mixed on-premises and cloud (hybrid) environments",
            "Evolving architectural requirements",
            "Prefer managed services over rearchitecting",
        ],
        typical_components=[
            "Web/Presentation tier", "Business logic/Middle tier",
            "Data tier", "Load balancers between tiers",
            "Web Application Firewall (WAF)", "Cache layer",
            "Message queue for async tier communication",
            "Network Security Groups (NSGs) per subnet",
            "Perimeter network / DMZ with NVAs",
            "Management subnet (Bastion for secure access)",
        ],
        azure_services=[
            "application_gateway", "vm_scale_set", "app_service",
            "sql_database", "redis_cache", "service_bus",
            "load_balancer", "bastion", "virtual_network",
            "nsg", "firewall", "expressroute",
        ],
        flow_direction="TB",
        layout_strategy="tiered",
        diagram_conventions=[
            "Arrange tiers top-to-bottom: WAF → Web → Business → Data",
            "Place each tier in its own subnet within a VNet boundary",
            "Show load balancers between tiers",
            "Use solid arrows for request flow downward",
            "Use dashed arrows for cached data access",
            "Include NSGs on every subnet for tier isolation",
            "Add management/bastion subnet for admin access",
            "Show perimeter network (DMZ) between internet and web tier",
        ],
    ),
    "web_queue_worker": ArchitectureStyle(
        key="web_queue_worker",
        name="Web-Queue-Worker",
        description=(
            "Architecture with a web front end handling HTTP requests, a message "
            "queue for decoupling, and a back-end worker processing resource-intensive "
            "tasks or long-running workflows. Front end and worker are stateless "
            "and scale independently. Worker is optional for simple read/write apps."
        ),
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/web-queue-worker",
        when_to_use=[
            "Relatively simple domains with resource-intensive tasks",
            "Applications with long-running workflows or batch operations",
            "Independent scaling of front end and workers",
            "Prefer managed services (PaaS) over IaaS",
        ],
        typical_components=[
            "Web front end (App Service)", "Message queue (Service Bus or Storage queues)",
            "Background worker (Functions app)", "Identity provider",
            "CDN for static content", "Database",
            "Distributed cache (Managed Redis)",
            "Blob storage for static assets",
            "Polyglot persistence (SQL + Cosmos DB)",
            "Remote services (email, SMS)",
        ],
        azure_services=[
            "app_service", "function_app", "service_bus",
            "storage_account", "sql_database", "redis_cache",
            "cdn_profile", "entra_id", "cosmos_db",
            "blob_storage",
        ],
        flow_direction="LR",
        layout_strategy="tiered",
        diagram_conventions=[
            "Place web front end on the left, worker on the right",
            "Show queue as the central decoupling mechanism between web and worker",
            "Identity provider connects to web front end",
            "CDN branches off for static content delivery",
            "Both web and worker connect to shared database/cache at the bottom",
            "Use separate App Service plans for web and worker for independent scaling",
            "Show polyglot persistence (SQL DB + Cosmos DB) when applicable",
        ],
    ),
    "microservices": ArchitectureStyle(
        key="microservices",
        name="Microservices",
        description=(
            "Application decomposed into small, autonomous services each implementing "
            "a single business capability within a DDD bounded context. Services "
            "communicate through well-defined APIs and message brokers, each owning "
            "its own data (polyglot persistence). Supports independent deployment, "
            "technology diversity, and fault isolation."
        ),
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/microservices",
        when_to_use=[
            "Complex domains requiring frequent updates",
            "Teams needing autonomous deployment capabilities",
            "Applications requiring independent service scaling",
            "Organizations with mature DevOps practices",
            "Need for technology diversity (polyglot programming)",
        ],
        typical_components=[
            "API Gateway (entry point, auth, logging, load balancing)",
            "Domain services (bounded contexts)",
            "Composition / aggregation services",
            "Message-oriented middleware (Kafka, Service Bus)",
            "Per-service databases — polyglot persistence (SQL + NoSQL)",
            "Container orchestration (Kubernetes / Container Apps)",
            "Sidecar proxy / Service mesh (Dapr, Envoy)",
            "Observability stack (OpenTelemetry, distributed tracing, metrics)",
            "CI/CD pipelines (per-service independent deploy)",
            "Management/orchestration component",
        ],
        azure_services=[
            "api_management", "kubernetes_service", "container_apps",
            "service_bus", "event_hub", "cosmos_db", "sql_database",
            "container_registry", "monitor", "application_insights",
            "key_vault", "entra_id", "virtual_network",
        ],
        flow_direction="LR",
        layout_strategy="tiered",
        diagram_conventions=[
            "API Gateway on the left as single entry point",
            "Group microservices in the center with individual databases",
            "Show message broker for async service-to-service communication",
            "Place observability/management layer at the bottom",
            "Each service gets its own database icon (polyglot persistence)",
            "Use dashed arrows for pub/sub event flows",
            "Keep domain knowledge out of the gateway",
            "Show circuit-breaker patterns on inter-service calls",
        ],
    ),
    "event_driven": ArchitectureStyle(
        key="event_driven",
        name="Event-Driven",
        description=(
            "Architecture where event producers generate streams of events consumed "
            "by independent event consumers via an event broker. Producers and consumers "
            "are fully decoupled. Two models: pub/sub (Event Grid — events not stored, "
            "subscribers filter) and event streaming (Event Hubs — durable ordered log, "
            "consumers replay). Two topologies: broker (broadcast, no orchestration) "
            "and mediator (centralized flow control)."
        ),
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven",
        when_to_use=[
            "Multiple subsystems processing the same events",
            "Real-time processing with minimal latency",
            "Complex event processing (pattern matching, aggregation over time windows)",
            "High-volume IoT or streaming data scenarios",
            "Decouple producers and consumers for independent scalability",
        ],
        typical_components=[
            "Event producers",
            "Event ingestion — pub/sub broker (Event Grid)",
            "Event ingestion — streaming log (Event Hubs / Kafka)",
            "Event consumers (multiple independent, scaled-out instances)",
            "Stream processing (simple, correlation, or complex)",
            "Dead-letter queue (DLQ) for failed events",
            "Error-handler processor (resubmit or escalate)",
            "Event store / durable log",
        ],
        azure_services=[
            "event_hub", "event_grid", "service_bus",
            "function_app", "stream_analytics", "cosmos_db",
            "storage_account", "iot_hub", "monitor",
            "application_insights",
        ],
        flow_direction="LR",
        layout_strategy="tiered",
        diagram_conventions=[
            "Producers on the left, broker in the center, consumers on the right",
            "Fan-out arrows from broker to multiple consumers",
            "Distinguish pub/sub (Event Grid) from streaming (Event Hubs) paths",
            "Include correlation IDs on event flows for traceability",
            "Show dead-letter queue for failed processing",
            "Use solid arrows for event flow direction",
            "Show error-handler processor loop for retry/resubmit",
        ],
    ),
    "big_data": ArchitectureStyle(
        key="big_data",
        name="Big Data",
        description=(
            "Architecture for ingesting, processing, and analyzing data too large "
            "for traditional databases. Includes batch processing for historical "
            "analysis (Lambda speed layer) and stream processing for real-time "
            "insights, with an orchestration layer spanning both pipelines. "
            "IoT is a specialized subset using event-streaming components."
        ),
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/big-data",
        when_to_use=[
            "Batch and real-time data analysis at scale",
            "Predictive analytics and machine learning",
            "Processing unstructured/semi-structured data",
            "IoT data ingestion and analytics",
            "Data too large for traditional RDBMS",
        ],
        typical_components=[
            "Data sources (databases, log files, real-time devices)",
            "Data lake / distributed file store",
            "Batch processing pipeline (ELT / ETL)",
            "Real-time message ingestion",
            "Stream processing (in-flight transforms)",
            "Analytical data store (warehouse, lakehouse, eventhouse)",
            "Analytics, reporting, and data modeling (OLAP / Power BI)",
            "Actions and alerting layer (proactive notifications)",
            "Orchestration layer (Data Factory / Fabric pipelines)",
        ],
        azure_services=[
            "data_lake_storage", "storage_account", "event_hub",
            "data_factory", "databricks", "synapse_analytics",
            "stream_analytics", "sql_database", "cosmos_db",
            "machine_learning", "monitor", "iot_hub",
            "log_analytics",
        ],
        flow_direction="LR",
        layout_strategy="tiered",
        diagram_conventions=[
            "Two parallel pipelines: batch (top) and real-time (bottom)",
            "Data sources on the left, analytics/reporting on the right",
            "Show orchestration layer spanning both pipelines",
            "Analytical data store feeds both pipelines to reporting",
            "Use numbered workflow steps for data flow",
            "Label batch vs real-time paths explicitly",
            "For IoT: add cloud gateway, field gateway, device registry",
        ],
    ),
    "big_compute": ArchitectureStyle(
        key="big_compute",
        name="Big Compute (HPC)",
        description=(
            "Architecture for large-scale workloads requiring hundreds or thousands "
            "of cores. Jobs are split into discrete tasks — either embarrassingly "
            "parallel (independent) or tightly coupled (requiring inter-process "
            "communication via InfiniBand/RDMA). Azure Batch provides managed "
            "scheduling and auto-scaling of VM pools; HPC Pack supports hybrid "
            "burst-to-cloud scenarios."
        ),
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/big-compute",
        when_to_use=[
            "Simulations and number crunching",
            "Financial risk modeling and Monte Carlo simulations",
            "Scientific computing and engineering stress analysis",
            "3D image rendering and media processing",
            "Long-running computations too slow for a single machine",
        ],
        typical_components=[
            "Job queue", "Scheduler/Coordinator (Batch or HPC Pack head node)",
            "Embarrassingly-parallel task workers",
            "Tightly-coupled task workers (InfiniBand/RDMA)",
            "Azure Batch managed VM pools",
            "Shared storage (Blob, file shares)",
            "High-speed network (InfiniBand for HBv5/HC/HX VMs)",
        ],
        azure_services=[
            "virtual_machine", "vm_scale_set", "storage_account",
            "blob_storage", "virtual_network",
        ],
        flow_direction="LR",
        layout_strategy="tiered",
        diagram_conventions=[
            "Client/job submission on the left",
            "Scheduler/coordinator (Azure Batch or HPC Pack) in the center",
            "Two branches: parallel tasks and tightly coupled tasks",
            "Show shared storage accessible by all workers",
            "Include VNet boundary around compute cluster",
            "For hybrid: show on-premises head node with ExpressRoute/VPN to Azure VMs",
        ],
    ),
}


# ── Azure Cloud Design Patterns ──────────────────────────────────
# Source: https://learn.microsoft.com/en-us/azure/architecture/patterns/
#
# These are the standard cloud design patterns from the Azure Architecture Center.
# Each pattern addresses a specific challenge in distributed cloud applications
# and maps to one or more WAF pillars.

@dataclass
class DesignPattern:
    """An Azure Architecture Center cloud design pattern."""
    key: str
    name: str
    description: str
    source_url: str
    waf_pillars: list[str]          # Which WAF pillars this pattern supports
    when_to_use: list[str]
    when_not_to_use: list[str]
    related_patterns: list[str]     # Keys of related patterns
    azure_services: list[str]       # Relevant Azure services
    diagram_implications: list[str]  # How this affects architecture diagrams


DESIGN_PATTERNS: dict[str, DesignPattern] = {
    "ambassador": DesignPattern(
        key="ambassador",
        name="Ambassador",
        description="Create helper services that send network requests on behalf of a consumer service or application. Offloads cross-cutting client connectivity tasks like monitoring, logging, routing, and security.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/ambassador",
        waf_pillars=["Reliability", "Security"],
        when_to_use=["Multiple languages/frameworks need common client connectivity features", "Offloading cross-cutting connectivity concerns to infrastructure or specialized teams"],
        when_not_to_use=["Single language — use a client library instead", "Latency overhead of the proxy is unacceptable"],
        related_patterns=["sidecar"],
        azure_services=["container_apps", "kubernetes_service"],
        diagram_implications=["Show ambassador as a sidecar adjacent to the main service", "Arrow from service → ambassador → external dependency"],
    ),
    "anti_corruption_layer": DesignPattern(
        key="anti_corruption_layer",
        name="Anti-Corruption Layer",
        description="Implement a façade or adapter layer between different subsystems that don't share the same semantics. Translates between modern and legacy systems, preventing legacy design from corrupting new application code.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer",
        waf_pillars=["Operational Excellence"],
        when_to_use=["Migration planned over multiple stages with new/legacy integration", "Two subsystems have different semantics but must communicate"],
        when_not_to_use=["No significant semantic differences between systems"],
        related_patterns=["strangler_fig"],
        azure_services=["logic_app", "api_management", "function_app"],
        diagram_implications=["Show ACL as a distinct box between legacy and modern subsystems", "Use different visual styles for legacy vs. modern components"],
    ),
    "async_request_reply": DesignPattern(
        key="async_request_reply",
        name="Asynchronous Request-Reply",
        description="Decouple backend processing from a frontend host, where backend processing needs to be asynchronous, but the frontend still needs a clear response.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/async-request-reply",
        waf_pillars=["Performance Efficiency", "Reliability"],
        when_to_use=["Client code difficult to provide callbacks", "Need HTTP-friendly response semantics with long-running backend work"],
        when_not_to_use=["Responses must be real-time", "Service-to-service calls where async messaging is simpler"],
        related_patterns=["publisher_subscriber"],
        azure_services=["function_app", "service_bus", "api_management"],
        diagram_implications=["Show request and polling/callback paths separately", "Include a status endpoint between client and backend"],
    ),
    "backends_for_frontends": DesignPattern(
        key="backends_for_frontends",
        name="Backends for Frontends",
        description="Create separate backend services for different types of clients (web, mobile, desktop). Each backend is tailored to the specific needs of its client UI.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends",
        waf_pillars=["Performance Efficiency", "Operational Excellence"],
        when_to_use=["Shared backend bloated by multiple client interface requirements", "Different clients need different backend behavior optimization"],
        when_not_to_use=["A single backend serves all clients adequately", "Clients don't have significantly different requirements"],
        related_patterns=["gateway_routing", "gateway_offloading"],
        azure_services=["app_service", "container_apps", "api_management"],
        diagram_implications=["Show separate backend boxes per client type (Web BFF, Mobile BFF)", "API Gateway routes traffic to appropriate BFF"],
    ),
    "bulkhead": DesignPattern(
        key="bulkhead",
        name="Bulkhead",
        description="Isolate elements of an application into pools so that if one fails, the others will continue to function. Named after bulkheads in ship hulls that limit flooding.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead",
        waf_pillars=["Reliability"],
        when_to_use=["Isolate resources used to consume backend services", "Protect critical consumers from cascading failure", "Isolate faults in individual tenants"],
        when_not_to_use=["Resource inefficiency is unacceptable", "Added complexity isn't necessary"],
        related_patterns=["circuit_breaker", "throttling"],
        azure_services=["kubernetes_service", "container_apps", "app_service"],
        diagram_implications=["Show separate resource pools/partitions with isolation boundaries", "Use distinct boundary boxes for each bulkhead partition"],
    ),
    "cache_aside": DesignPattern(
        key="cache_aside",
        name="Cache-Aside",
        description="Load data on demand into a cache from a data store. Improves performance and helps maintain consistency between cached data and the underlying data store.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside",
        waf_pillars=["Reliability", "Performance Efficiency"],
        when_to_use=["Cache doesn't provide native read-through/write-through", "Resource demand is unpredictable — load data on demand"],
        when_not_to_use=["Cached data set is static — prime cache on startup", "Most requests are cache misses", "Data is sensitive or security-related"],
        related_patterns=[],
        azure_services=["redis_cache", "cosmos_db", "sql_database"],
        diagram_implications=["Show cache as a separate component between app and data store", "Numbered arrows: 1) check cache, 2) cache miss → read store, 3) populate cache"],
    ),
    "choreography": DesignPattern(
        key="choreography",
        name="Choreography",
        description="Let each service decide when and how a business operation is processed, instead of depending on a central orchestrator. Services communicate through events.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/choreography",
        waf_pillars=["Reliability", "Performance Efficiency"],
        when_to_use=["Simple workflows with few services that don't need coordination", "No single point of failure desired"],
        when_not_to_use=["Workflow is complex with many steps", "Need centralized error handling or compensation"],
        related_patterns=["saga", "publisher_subscriber"],
        azure_services=["event_grid", "service_bus", "event_hub"],
        diagram_implications=["Show peer-to-peer event flows between services", "No central orchestrator — events fan out from each service"],
    ),
    "circuit_breaker": DesignPattern(
        key="circuit_breaker",
        name="Circuit Breaker",
        description="Handle faults that might take a variable amount of time to recover from when connecting to a remote service. Prevents an application from repeatedly trying an operation likely to fail.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker",
        waf_pillars=["Reliability", "Performance Efficiency"],
        when_to_use=["Prevent cascading failures from excessive remote service calls", "Protect against slow dependencies to maintain SLOs", "Route traffic based on real-time failure signals"],
        when_not_to_use=["Managing access to local private resources — adds overhead", "As a substitute for business logic exception handling", "Message-driven architectures with built-in failure isolation"],
        related_patterns=["retry", "bulkhead"],
        azure_services=["app_service", "container_apps", "cosmos_db"],
        diagram_implications=["Show circuit breaker as an inline component between caller and remote service", "State diagram: Closed → Open → Half-Open"],
    ),
    "claim_check": DesignPattern(
        key="claim_check",
        name="Claim Check",
        description="Split a large message into a claim check and a payload. Store payload in external storage and send only the claim check to the messaging platform.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/claim-check",
        waf_pillars=["Performance Efficiency", "Cost Optimization"],
        when_to_use=["Message bus has size limits", "Large payloads should not flow through the message bus"],
        when_not_to_use=["Message payloads are small enough for the bus"],
        related_patterns=["publisher_subscriber"],
        azure_services=["service_bus", "event_grid", "storage_account", "blob_storage"],
        diagram_implications=["Show two paths: small claim-check message through bus, large payload stored separately", "Arrow from sender → storage for payload, sender → bus for claim check"],
    ),
    "compensating_transaction": DesignPattern(
        key="compensating_transaction",
        name="Compensating Transaction",
        description="Undo the work performed by a series of steps when one or more steps fail. Particularly relevant for eventually consistent operations in cloud-hosted applications.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction",
        waf_pillars=["Reliability"],
        when_to_use=["Steps in eventual consistency model must be undone on failure", "Complex business processes require rollback semantics"],
        when_not_to_use=["Operations are fully transactional (ACID)"],
        related_patterns=["saga", "event_sourcing"],
        azure_services=["function_app", "logic_app", "service_bus"],
        diagram_implications=["Show compensating step arrows in reverse direction from normal flow", "Use different arrow style for compensation path"],
    ),
    "competing_consumers": DesignPattern(
        key="competing_consumers",
        name="Competing Consumers",
        description="Enable multiple concurrent consumers to process messages received on the same messaging channel. Improves throughput and scalability.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/competing-consumers",
        waf_pillars=["Performance Efficiency", "Reliability"],
        when_to_use=["Application workload is divisible into independent tasks", "Tasks must be processed concurrently at variable throughput"],
        when_not_to_use=["Application needs to process individual messages in order"],
        related_patterns=["queue_based_load_leveling", "priority_queue"],
        azure_services=["service_bus", "event_hub", "function_app"],
        diagram_implications=["Show multiple consumer instances reading from a single queue", "Fan-out from queue to N consumer replicas"],
    ),
    "cqrs": DesignPattern(
        key="cqrs",
        name="CQRS",
        description="Command Query Responsibility Segregation — separate read and write operations for a data store into separate data models. Each model can be optimized independently for performance, scalability, and security.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs",
        waf_pillars=["Performance Efficiency"],
        when_to_use=["Collaborative environments with concurrent data access", "Task-based UIs with complex domain models", "Read performance must be tuned separately from write performance", "Development teams need to work independently on read/write models"],
        when_not_to_use=["Domain or business rules are simple", "Simple CRUD-style interface is sufficient"],
        related_patterns=["event_sourcing"],
        azure_services=["cosmos_db", "sql_database", "event_hub", "service_bus", "redis_cache"],
        diagram_implications=["Show separate read model and write model with distinct data stores", "Command path on one side, query path on the other", "Event sync path between write store and read store"],
    ),
    "deployment_stamps": DesignPattern(
        key="deployment_stamps",
        name="Deployment Stamps",
        description="Deploy multiple independent copies of application components, including data stores. Each stamp serves a subset of tenants or requests.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/deployment-stamp",
        waf_pillars=["Reliability", "Performance Efficiency"],
        when_to_use=["Multi-tenant systems needing isolation", "Geographically distributed deployments", "Scaling beyond single deployment limits"],
        when_not_to_use=["Single-region, single-tenant deployment is sufficient"],
        related_patterns=["sharding"],
        azure_services=["front_door", "traffic_manager", "container_apps", "sql_database"],
        diagram_implications=["Show multiple identical stamp rectangles with a global load balancer in front", "Each stamp contains the full application stack"],
    ),
    "event_sourcing": DesignPattern(
        key="event_sourcing",
        name="Event Sourcing",
        description="Store the full series of actions taken on an object in an append-only store instead of just the current state. The store acts as the system of record for materializing domain objects. Provides auditability and replay capability.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing",
        waf_pillars=["Reliability", "Performance Efficiency"],
        when_to_use=["Need to capture intent, purpose, or reason in data changes", "Minimize conflicting updates to data", "Need event replay for audit, rollback, or state reconstruction", "Decouple input processing from task execution"],
        when_not_to_use=["Simple CRUD without auditability or replay requirements", "Prototypes or MVPs with short expected lifespans", "Systems requiring real-time consistency", "Mostly static or reference data"],
        related_patterns=["cqrs", "compensating_transaction"],
        azure_services=["event_hub", "cosmos_db", "service_bus", "storage_account"],
        diagram_implications=["Show append-only event store as the write model", "Separate read projections/materialized views", "Usually combined with CQRS: present both read and write paths"],
    ),
    "external_configuration_store": DesignPattern(
        key="external_configuration_store",
        name="External Configuration Store",
        description="Move configuration information out of application deployment packages to a centralized location for easier management and control.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/external-configuration-store",
        waf_pillars=["Operational Excellence"],
        when_to_use=["Config shared by multiple applications", "Centralized management and auditing of configuration"],
        when_not_to_use=["Simple applications with minimal configuration"],
        related_patterns=["throttling"],
        azure_services=["key_vault"],
        diagram_implications=["Show centralized config store accessed by multiple application instances"],
    ),
    "federated_identity": DesignPattern(
        key="federated_identity",
        name="Federated Identity",
        description="Delegate authentication to an external identity provider to simplify development, minimize user administration, and improve UX.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/federated-identity",
        waf_pillars=["Security"],
        when_to_use=["Single sign-on across multiple applications", "Integration with corporate or social identity providers"],
        when_not_to_use=["Application has sole control over user credentials"],
        related_patterns=[],
        azure_services=["entra_id", "api_management"],
        diagram_implications=["Show external IdP with federated trust arrow to application", "Dashed line for identity/auth flow"],
    ),
    "gateway_aggregation": DesignPattern(
        key="gateway_aggregation",
        name="Gateway Aggregation",
        description="Use a gateway to aggregate multiple individual requests into a single request. Reduces chattiness between the client and backend services.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation",
        waf_pillars=["Performance Efficiency"],
        when_to_use=["Client needs to call multiple backend services", "Reduce round trips and latency for clients"],
        when_not_to_use=["Single backend service is sufficient"],
        related_patterns=["gateway_offloading", "gateway_routing", "backends_for_frontends"],
        azure_services=["api_management", "application_gateway", "front_door"],
        diagram_implications=["Show gateway as single entry point with fan-out to multiple backends", "Single arrow from client to gateway, multiple arrows from gateway to services"],
    ),
    "gateway_offloading": DesignPattern(
        key="gateway_offloading",
        name="Gateway Offloading",
        description="Offload shared or specialized service functionality to a gateway proxy. Simplifies application development by moving cross-cutting concerns like SSL, auth, and throttling to the gateway.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-offloading",
        waf_pillars=["Reliability", "Security", "Cost Optimization", "Operational Excellence", "Performance Efficiency"],
        when_to_use=["Shared concerns like SSL certificates or encryption", "Features common across deployments with different resource requirements", "Moving network boundary concerns to a specialized team"],
        when_not_to_use=["Would introduce coupling across services"],
        related_patterns=["gateway_aggregation", "gateway_routing"],
        azure_services=["application_gateway", "front_door", "api_management"],
        diagram_implications=["Show gateway handling SSL termination, WAF, and auth before reaching backend", "Label offloaded functions on the gateway box"],
    ),
    "gateway_routing": DesignPattern(
        key="gateway_routing",
        name="Gateway Routing",
        description="Route requests to multiple services using a single endpoint. Useful when exposing multiple services on a single endpoint and routing based on the request.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-routing",
        waf_pillars=["Operational Excellence"],
        when_to_use=["Single endpoint for multiple services", "Path- or header-based routing to backend services"],
        when_not_to_use=["Simple application with one backend"],
        related_patterns=["gateway_aggregation", "gateway_offloading"],
        azure_services=["application_gateway", "front_door", "api_management"],
        diagram_implications=["Show single gateway → multiple backend routes based on path rules", "Label routing rules on arrows"],
    ),
    "geode": DesignPattern(
        key="geode",
        name="Geode",
        description="Deploy backend services into a set of geographical nodes, each of which can service any client request in any region. Active-active pattern for global distribution.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/geodes",
        waf_pillars=["Reliability", "Performance Efficiency"],
        when_to_use=["Globally distributed application with active-active requirements", "Low-latency access for users in multiple regions"],
        when_not_to_use=["Single-region deployment is sufficient"],
        related_patterns=["deployment_stamps"],
        azure_services=["front_door", "cosmos_db", "traffic_manager"],
        diagram_implications=["Show multiple regional deployments with global load balancer", "Each region contains identical stack — use region boundary boxes"],
    ),
    "health_endpoint_monitoring": DesignPattern(
        key="health_endpoint_monitoring",
        name="Health Endpoint Monitoring",
        description="Implement functional checks in an application that external tools can access through exposed endpoints at regular intervals.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/health-endpoint-monitoring",
        waf_pillars=["Reliability", "Operational Excellence"],
        when_to_use=["Monitor availability and correct operation of applications and services", "Monitoring via load balancers and health checks"],
        when_not_to_use=["Direct application logging is sufficient"],
        related_patterns=["circuit_breaker"],
        azure_services=["monitor", "application_insights", "front_door", "load_balancer"],
        diagram_implications=["Show health probe arrows from monitoring service to application endpoints", "Include /health endpoint on service boxes"],
    ),
    "leader_election": DesignPattern(
        key="leader_election",
        name="Leader Election",
        description="Coordinate actions performed by a collection of collaborating instances by electing one instance as the leader to manage the others.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/leader-election",
        waf_pillars=["Reliability"],
        when_to_use=["Multiple identical instances with one needing to coordinate", "Task requires a single coordinator from a peer group"],
        when_not_to_use=["A dedicated coordinator service is simpler"],
        related_patterns=[],
        azure_services=["storage_account", "cosmos_db", "redis_cache"],
        diagram_implications=["Show one instance highlighted as 'leader' among peer replicas", "Lease/lock arrow to a shared store for election"],
    ),
    "materialized_view": DesignPattern(
        key="materialized_view",
        name="Materialized View",
        description="Generate prepopulated views over data in one or more data stores when the data isn't ideally formatted for required query operations.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view",
        waf_pillars=["Performance Efficiency"],
        when_to_use=["Complex queries that benefit from precomputed results", "Read access patterns differ significantly from write patterns"],
        when_not_to_use=["Source data is simple and easy to query", "Data changes frequently making views stale"],
        related_patterns=["cqrs", "event_sourcing"],
        azure_services=["cosmos_db", "sql_database", "redis_cache"],
        diagram_implications=["Show read-optimized view store separate from source data store", "Projection arrow from source to materialized view"],
    ),
    "pipes_and_filters": DesignPattern(
        key="pipes_and_filters",
        name="Pipes and Filters",
        description="Decompose a complex processing task into a series of reusable elements (filters) connected by channels (pipes). Each filter performs one transformation step.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/pipes-and-filters",
        waf_pillars=["Performance Efficiency", "Operational Excellence"],
        when_to_use=["Processing can be decomposed into discrete, reusable steps", "Steps have different scalability requirements"],
        when_not_to_use=["Steps are tightly coupled or must share state"],
        related_patterns=["competing_consumers"],
        azure_services=["function_app", "service_bus", "event_hub"],
        diagram_implications=["Show linear pipeline: Filter A → Queue → Filter B → Queue → Filter C", "Each filter is a separate service/function box"],
    ),
    "priority_queue": DesignPattern(
        key="priority_queue",
        name="Priority Queue",
        description="Prioritize requests sent to services so that requests with a higher priority are received and processed more quickly than those with a lower priority.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/priority-queue",
        waf_pillars=["Performance Efficiency"],
        when_to_use=["Different SLAs for different clients or message types", "Critical messages need faster processing"],
        when_not_to_use=["All messages have equal priority"],
        related_patterns=["competing_consumers", "throttling", "queue_based_load_leveling"],
        azure_services=["service_bus"],
        diagram_implications=["Show multiple queue lanes (high/low priority) with different consumer pools", "Label priority levels on queues"],
    ),
    "publisher_subscriber": DesignPattern(
        key="publisher_subscriber",
        name="Publisher-Subscriber",
        description="Enable an application to broadcast events asynchronously to multiple interested consumers without coupling senders and receivers. Decouples subsystems through a message broker.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber",
        waf_pillars=["Reliability", "Security", "Cost Optimization", "Operational Excellence", "Performance Efficiency"],
        when_to_use=["Broadcast information to many consumers", "Integrate systems using different platforms or protocols", "Eventual consistency model for data", "Consumers with different availability requirements"],
        when_not_to_use=["Few consumers needing different information — direct communication simpler", "Near real-time interaction required", "Must process messages in strict guaranteed order"],
        related_patterns=["competing_consumers", "queue_based_load_leveling"],
        azure_services=["service_bus", "event_grid", "event_hub"],
        diagram_implications=["Show publisher → message broker → fan-out to multiple subscribers", "Use topic/subscription labels on broker", "Include Azure Service Bus, Event Grid, or Event Hubs as broker"],
    ),
    "queue_based_load_leveling": DesignPattern(
        key="queue_based_load_leveling",
        name="Queue-Based Load Leveling",
        description="Use a queue that acts as a buffer between a task and a service to smooth intermittent heavy loads that can cause the service to fail or time out.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling",
        waf_pillars=["Reliability", "Cost Optimization", "Performance Efficiency"],
        when_to_use=["Application uses services subject to overloading", "Buffer intermittent load spikes"],
        when_not_to_use=["Application expects response with minimal latency"],
        related_patterns=["competing_consumers", "throttling", "priority_queue"],
        azure_services=["service_bus", "function_app"],
        diagram_implications=["Show queue between task producers and service consumers", "Label the queue as a load-leveling buffer"],
    ),
    "rate_limiting": DesignPattern(
        key="rate_limiting",
        name="Rate Limiting",
        description="Control the rate at which an application, service, or entire system engages with a resource to avoid throttling errors and manage costs.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/rate-limiting-pattern",
        waf_pillars=["Reliability", "Cost Optimization"],
        when_to_use=["Reduce throttling errors from downstream services", "Control resource consumption and costs"],
        when_not_to_use=["Target system handles backpressure natively"],
        related_patterns=["throttling", "queue_based_load_leveling"],
        azure_services=["api_management", "redis_cache"],
        diagram_implications=["Show rate limiter as an inline component before the target service", "Label with rate limit configuration"],
    ),
    "retry": DesignPattern(
        key="retry",
        name="Retry",
        description="Enable an application to handle transient failures when it tries to connect to a service or network resource, by transparently retrying a failed operation. Improves application stability.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/retry",
        waf_pillars=["Reliability"],
        when_to_use=["Application experiences transient faults connecting to remote services", "Faults are expected to be short-lived"],
        when_not_to_use=["Fault is likely to be long-lasting — use circuit breaker instead", "Handling non-transient internal errors"],
        related_patterns=["circuit_breaker"],
        azure_services=["app_service", "function_app", "cosmos_db", "sql_database"],
        diagram_implications=["Show retry loop arrow on the calling service", "Annotate with retry policy (exponential backoff)"],
    ),
    "saga": DesignPattern(
        key="saga",
        name="Saga",
        description="Manage data consistency across microservices in distributed transactions. A saga is a sequence of local transactions where each service performs its operation and triggers the next via events. Failed steps trigger compensating transactions.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/saga",
        waf_pillars=["Reliability"],
        when_to_use=["Ensure data consistency in distributed systems without tight coupling", "Need rollback/compensation when operations in a sequence fail"],
        when_not_to_use=["Transactions are tightly coupled", "Cyclic dependencies between participants"],
        related_patterns=["choreography", "compensating_transaction", "retry"],
        azure_services=["function_app", "logic_app", "service_bus", "event_grid"],
        diagram_implications=["Choreography: show peer events between services", "Orchestration: show central orchestrator directing each service step", "Include compensating transaction arrows (reverse direction, dashed)"],
    ),
    "sharding": DesignPattern(
        key="sharding",
        name="Sharding",
        description="Divide a data store into a set of horizontal partitions or shards. Each shard has the same schema but holds its own distinct subset of data.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding",
        waf_pillars=["Performance Efficiency"],
        when_to_use=["Data store exceeds single node capacity", "Reduce contention by distributing load across shards"],
        when_not_to_use=["Data fits within a single node", "Cross-shard queries are common"],
        related_patterns=["deployment_stamps"],
        azure_services=["cosmos_db", "sql_database"],
        diagram_implications=["Show data store split into multiple shard boxes", "Routing logic box directing queries to appropriate shard"],
    ),
    "sidecar": DesignPattern(
        key="sidecar",
        name="Sidecar",
        description="Deploy application components into a separate process or container alongside the main application to provide isolation and encapsulation. Enables platform services across polyglot applications.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar",
        waf_pillars=["Security", "Operational Excellence", "Performance Efficiency"],
        when_to_use=["Diverse languages/frameworks need consistent cross-cutting features", "Separate team owns a component", "Need fine-grained resource control for a specific component"],
        when_not_to_use=["Interprocess communication overhead is unacceptable", "Application is small — resource cost outweighs isolation benefit", "Platform already provides the needed capabilities natively"],
        related_patterns=["ambassador"],
        azure_services=["kubernetes_service", "container_apps"],
        diagram_implications=["Show sidecar container adjacent to main app container within same pod/host", "Both share a host boundary box", "Sidecar handles logging, proxy, config, etc."],
    ),
    "static_content_hosting": DesignPattern(
        key="static_content_hosting",
        name="Static Content Hosting",
        description="Deploy static content to a cloud-based storage service that can deliver them directly to the client. Reduces need for expensive compute resources.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/static-content-hosting",
        waf_pillars=["Cost Optimization", "Performance Efficiency"],
        when_to_use=["Serving static files (HTML, CSS, JS, images)", "Reduce compute costs for static content delivery"],
        when_not_to_use=["Content requires server-side processing"],
        related_patterns=[],
        azure_services=["storage_account", "cdn_profile", "static_web_app"],
        diagram_implications=["Show CDN/storage for static content separate from compute for API", "CDN edge node in front of storage"],
    ),
    "strangler_fig": DesignPattern(
        key="strangler_fig",
        name="Strangler Fig",
        description="Incrementally migrate a legacy system by gradually replacing specific pieces of functionality with new applications and services. A façade intercepts requests and routes them to legacy or new services.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig",
        waf_pillars=["Reliability", "Cost Optimization", "Operational Excellence"],
        when_to_use=["Gradually migrating a backend application to new architecture", "Original system can continue during extended migration"],
        when_not_to_use=["Back-end requests can't be intercepted", "Replacing the whole system is simpler"],
        related_patterns=["anti_corruption_layer"],
        azure_services=["api_management", "application_gateway", "front_door", "app_service"],
        diagram_implications=["Show façade/proxy routing to both legacy and modern systems", "Gradually shift arrows from legacy to modern over phases"],
    ),
    "throttling": DesignPattern(
        key="throttling",
        name="Throttling",
        description="Control the consumption of resources used by an application, tenant, or service. Allows the system to continue functioning and meet SLOs even under extreme load.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/throttling",
        waf_pillars=["Reliability", "Security", "Cost Optimization", "Performance Efficiency"],
        when_to_use=["Ensure system meets SLOs", "Prevent single tenant from monopolizing resources", "Handle bursts and cost-optimize with resource limits"],
        when_not_to_use=["System handles load natively without degradation"],
        related_patterns=["queue_based_load_leveling", "priority_queue", "rate_limiting"],
        azure_services=["api_management", "app_service", "function_app"],
        diagram_implications=["Show throttling component (429/503 responses) before backend services", "Label with per-tenant or per-endpoint limits"],
    ),
    "valet_key": DesignPattern(
        key="valet_key",
        name="Valet Key",
        description="Use a token that provides clients with restricted direct access to a specific resource, to offload data transfer from the application.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/patterns/valet-key",
        waf_pillars=["Security", "Performance Efficiency"],
        when_to_use=["Minimize resource usage by offloading file transfers", "Give clients direct resource access with time-limited tokens"],
        when_not_to_use=["Application must control all data access"],
        related_patterns=["static_content_hosting"],
        azure_services=["storage_account", "blob_storage", "key_vault"],
        diagram_implications=["Show app generating SAS token, client using token to access storage directly", "Two-step flow: 1) request token, 2) direct access with token"],
    ),
    # ═══ New design patterns (grounded from Azure GitHub org review) ═══
    "medallion_architecture": DesignPattern(
        key="medallion_architecture",
        name="Medallion Architecture (Bronze/Silver/Gold)",
        description="A data design pattern that organizes data in a lakehouse into three layers: Bronze (raw ingestion), Silver (cleansed/conformed), and Gold (curated business-level aggregates). Enables incremental data quality improvement.",
        source_url="https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion",
        waf_pillars=["Operational Excellence", "Performance Efficiency", "Reliability"],
        when_to_use=["Building analytics platforms with data lakehouse", "Incremental ETL with data quality tiers", "Need auditability of raw data alongside curated views"],
        when_not_to_use=["Simple OLTP applications", "Real-time streaming with no batch analytics"],
        related_patterns=["pipes_and_filters", "event_sourcing"],
        azure_services=["databricks", "data_lake_storage", "synapse_analytics", "data_factory", "purview"],
        diagram_implications=["Show three layers left-to-right: Bronze → Silver → Gold", "Each layer in a separate boundary or swimlane", "Data Factory/Databricks arrows between layers"],
    ),
    "zero_trust_network": DesignPattern(
        key="zero_trust_network",
        name="Zero Trust Network",
        description="Assume breach; verify explicitly. Every network flow is authenticated, authorized, and encrypted regardless of source location. Micro-segmentation, least-privilege access, and continuous verification.",
        source_url="https://learn.microsoft.com/en-us/security/zero-trust/azure-networking",
        waf_pillars=["Security", "Reliability"],
        when_to_use=["Enterprise workloads requiring strict security posture", "Hybrid/multi-cloud environments", "Compliance-driven architectures (PCI-DSS, HIPAA)"],
        when_not_to_use=["Simple dev/test environments where overhead is unjustified"],
        related_patterns=["gateway_routing", "ambassador"],
        azure_services=["firewall", "private_endpoint", "nsg", "application_gateway", "entra_id", "managed_identity", "key_vault", "defender_for_cloud", "sentinel"],
        diagram_implications=["Every PaaS service connects via private endpoint", "No public IPs on workload resources", "NSG on every subnet", "Firewall as central egress/ingress point", "Show identity verification on all flows"],
    ),
    "policy_as_code": DesignPattern(
        key="policy_as_code",
        name="Policy as Code",
        description="Define, manage, and enforce organizational policies through code (Azure Policy, OPA/Gatekeeper). Enables consistent governance, automated compliance checks, and drift detection across subscriptions.",
        source_url="https://learn.microsoft.com/en-us/azure/governance/policy/concepts/policy-as-code",
        waf_pillars=["Operational Excellence", "Security"],
        when_to_use=["Enterprise governance at scale", "Enforcing tagging, SKU restrictions, region constraints", "Compliance reporting for auditors"],
        when_not_to_use=["Single-subscription sandbox environments"],
        related_patterns=["external_configuration_store"],
        azure_services=["policy", "blueprint", "management_group", "devops", "github_actions"],
        diagram_implications=["Show Policy as a governance layer above subscriptions", "Arrows from management group → subscription showing policy inheritance", "CI/CD pipeline deploying policy definitions"],
    ),
    "change_data_capture": DesignPattern(
        key="change_data_capture",
        name="Change Data Capture (CDC)",
        description="Capture row-level changes in source databases and propagate them to downstream systems in near real-time. Enables event-driven data pipelines without polling.",
        source_url="https://learn.microsoft.com/en-us/azure/cosmos-db/change-feed",
        waf_pillars=["Performance Efficiency", "Reliability"],
        when_to_use=["Real-time data synchronization between operational and analytical stores", "Event-driven architectures triggered by data changes", "Maintaining read replicas or materialized views"],
        when_not_to_use=["Batch-only analytics where latency is acceptable", "Simple CRUD apps without downstream consumers"],
        related_patterns=["event_sourcing", "cqrs", "materialized_view"],
        azure_services=["cosmos_db", "sql_database", "event_hub", "data_factory", "stream_analytics", "databricks"],
        diagram_implications=["Show change feed arrow from source DB to event stream", "Downstream consumers reading from event stream", "Separate read and write paths"],
    ),
}


def get_design_pattern(key: str) -> DesignPattern | None:
    """Look up a design pattern by key."""
    return DESIGN_PATTERNS.get(key)


def list_design_patterns() -> list[dict[str, Any]]:
    """List all available cloud design patterns."""
    return [
        {
            "key": p.key,
            "name": p.name,
            "description": p.description,
            "source_url": p.source_url,
            "waf_pillars": p.waf_pillars,
        }
        for p in DESIGN_PATTERNS.values()
    ]


def suggest_patterns_for_description(description: str) -> list[dict[str, Any]]:
    """Suggest design patterns based on a workload or challenge description.

    Performs keyword matching against pattern descriptions, use-cases,
    related services, and diagram implications.
    """
    desc_lower = description.lower()
    scored: list[tuple[int, DesignPattern]] = []

    for pattern in DESIGN_PATTERNS.values():
        score = 0
        # Pattern name match
        if pattern.key.replace("_", " ") in desc_lower:
            score += 10
        for word in pattern.name.lower().split():
            if len(word) > 3 and word in desc_lower:
                score += 3
        # Description keywords
        for word in pattern.description.lower().split():
            if len(word) > 5 and word in desc_lower:
                score += 1
        # When to use
        for use_case in pattern.when_to_use:
            for word in use_case.lower().split():
                if len(word) > 4 and word in desc_lower:
                    score += 1
        # Azure services
        for svc in pattern.azure_services:
            svc_name = svc.replace("_", " ")
            if svc_name in desc_lower:
                score += 2
        # WAF pillars
        for pillar in pattern.waf_pillars:
            if pillar.lower() in desc_lower:
                score += 2
        if score > 0:
            scored.append((score, pattern))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "key": p.key,
            "name": p.name,
            "score": score,
            "description": p.description,
            "waf_pillars": p.waf_pillars,
            "when_to_use": p.when_to_use,
            "when_not_to_use": p.when_not_to_use,
            "azure_services": p.azure_services,
            "related_patterns": p.related_patterns,
            "diagram_implications": p.diagram_implications,
        }
        for score, p in scored[:5]
    ]




# ═══════════════════════════════════════════════════════════════════
# AZURE ARCHITECTURE CATALOG — 206 reference architectures & solutions
# ═══════════════════════════════════════════════════════════════════
# Extracted from https://learn.microsoft.com/en-us/azure/architecture/browse/
# Each entry has: key, name, summary, source_url, type, categories, products

@dataclass
class AzureArchitectureEntry:
    """A reference architecture or solution idea from Azure Architecture Center."""
    key: str
    name: str
    summary: str
    source_url: str
    entry_type: str   # Architecture, Reference Architecture, Solution Idea, Best Practice
    categories: list[str]
    products: list[str]


AZURE_ARCHITECTURE_CATALOG: dict[str, AzureArchitectureEntry] = {
    "automate_document_classification_durable_functions": AzureArchitectureEntry(
        key="automate_document_classification_durable_functions",
        name="Automate document classification in Azure",
        summary="Learn how to use the durable functions feature of Azure Functions as an automated document processing pipeline to classify documents by type.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/automate-document-classification-durable-functions",
        entry_type="Architecture",
        categories=['AI + Machine Learning'],
        products=['azure-functions', 'microsoft-foundry', 'azure-ai-foundry-sdk', 'foundry-tools', 'azure-cognitive-search'],
    ),
    "analyze_video_computer_vision_machine_learning": AzureArchitectureEntry(
        key="analyze_video_computer_vision_machine_learning",
        name="Automate video analysis by using Azure Machine Learning and Azure Vision in Foundry Tools",
        summary="Learn how to implement an architecture that automates video analysis by using Azure Machine Learning and Azure Vision in Foundry Tools.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/analyze-video-computer-vision-machine-learning",
        entry_type="Architecture",
        categories=['AI + Machine Learning', 'Media'],
        products=['azure-machine-learning', 'foundry-tools', 'azure-logic-apps', 'azure-data-lake-storage', 'fabric'],
    ),
    "baseline_microsoft_foundry_chat": AzureArchitectureEntry(
        key="baseline_microsoft_foundry_chat",
        name="Baseline Microsoft Foundry chat reference architecture",
        summary="Learn how to build network-secured, highly available, and zone-redundant enterprise chat applications by using Microsoft Foundry tools and Azure App Service.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat",
        entry_type="Reference Architecture",
        categories=['AI + Machine Learning', 'Web', 'Networking', 'Security'],
        products=['foundry-tools', 'azure-app-service', 'azure-monitor', 'microsoft-foundry', 'foundry-agent-service'],
    ),
    "baseline_microsoft_foundry_landing_zone": AzureArchitectureEntry(
        key="baseline_microsoft_foundry_landing_zone",
        name="Baseline Microsoft Foundry chat reference architecture in an Azure landing zone",
        summary="Learn about deploying the baseline Microsoft Foundry, Foundry Agent Service, Azure OpenAI in Foundry Models, and Azure App Service chat architecture in an Azure landing zone.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-landing-zone",
        entry_type="Reference Architecture",
        categories=['AI + Machine Learning', 'Web', 'Networking', 'Security'],
        products=['azure-openai', 'foundry-tools', 'azure-app-service', 'azure-key-vault', 'azure-monitor'],
    ),
    "basic_microsoft_foundry_chat": AzureArchitectureEntry(
        key="basic_microsoft_foundry_chat",
        name="Basic Microsoft Foundry chat reference architecture",
        summary="Establish foundational knowledge for how to build and deploy enterprise chat applications by using Microsoft Foundry and Azure App Service.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/basic-microsoft-foundry-chat",
        entry_type="Reference Architecture",
        categories=['AI + Machine Learning', 'Web', 'Security'],
        products=['azure-app-service', 'azure-monitor', 'microsoft-foundry', 'foundry-agent-service', 'azure-ai-foundry-sdk'],
    ),
    "unlock_insights_from_conversational_data": AzureArchitectureEntry(
        key="unlock_insights_from_conversational_data",
        name="Build a conversation knowledge mining solution by using Foundry Tools",
        summary="Learn how to design a scalable conversation analytics system that extracts insights from conversational data by using Foundry Tools and Microsoft Foundry.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/unlock-insights-from-conversational-data",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning'],
        products=['foundry-tools', 'azure-container-apps', 'azure-cosmos-db', 'semantic-kernel', 'microsoft-foundry'],
    ),
    "multiple_agent_workflow_automation": AzureArchitectureEntry(
        key="multiple_agent_workflow_automation",
        name="Build a multiple-agent workflow automation solution by using Microsoft Agent Framework",
        summary="Learn how to design scalable automation pipelines where multiple AI agents collaborate by using Microsoft Agent Framework and Azure Container Apps for enterprise-grade tasks.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/multiple-agent-workflow-automation",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning'],
        products=['azure-container-apps', 'azure-cognitive-search', 'foundry-tools', 'azure-cosmos-db', 'microsoft-foundry'],
    ),
    "build_deploy_custom_models": AzureArchitectureEntry(
        key="build_deploy_custom_models",
        name="Build and deploy custom document processing models on Azure",
        summary="Learn more about Azure options for orchestrating, storing, building, deploying, and using custom document processing models.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/build-deploy-custom-models",
        entry_type="Architecture",
        categories=['AI + Machine Learning'],
        products=['document-intelligence', 'foundry-tools', 'azure-logic-apps', 'azure-machine-learning-studio', 'microsoft-foundry'],
    ),
    "azure_databricks_modern_analytics_architecture": AzureArchitectureEntry(
        key="azure_databricks_modern_analytics_architecture",
        name="Create a modern analytics architecture by using Azure Databricks",
        summary="Learn how to create a modern analytics architecture by using Azure Databricks, Data Lake Storage, and other Azure services. Unify data, analytics, and AI workloads at any scale.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/azure-databricks-modern-analytics-architecture",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning', 'Analytics'],
        products=['azure-databricks', 'fabric', 'power-bi', 'azure-data-lake-storage'],
    ),
    "secure_compute_for_research": AzureArchitectureEntry(
        key="secure_compute_for_research",
        name="Design a secure research environment for regulated data",
        summary="Learn how to design an architecture on Azure for a regulated environment that allows researchers to access sensitive data.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/secure-compute-for-research",
        entry_type="Architecture",
        categories=['AI + Machine Learning', 'Compute', 'Security'],
        products=['azure-data-science-vm', 'azure-machine-learning', 'fabric'],
    ),
    "multi_modal_content_processing": AzureArchitectureEntry(
        key="multi_modal_content_processing",
        name="Extract and map information from unstructured content",
        summary="Learn how to build scalable systems for processing text, images, tables, and graphs with quality checks and human review for professional content workflows.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/multi-modal-content-processing",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning'],
        products=['foundry-tools', 'azure-cosmos-db', 'azure-container-apps', 'microsoft-foundry'],
    ),
    "extract_object_text": AzureArchitectureEntry(
        key="extract_object_text",
        name="Extract text from objects using Power Automate and AI Builder",
        summary="Use AI Builder and Azure Document Intelligence in Foundry Tools in a Power Automate workflow to extract text from images, for indexing and retrieval.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/ai/extract-object-text",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning'],
        products=['ai-builder', 'document-intelligence', 'power-automate', 'power-platform', 'azure-functions'],
    ),
    "generate_documents_from_your_data": AzureArchitectureEntry(
        key="generate_documents_from_your_data",
        name="Generate documents from your data",
        summary="Learn how to build a simple system for generating document templates by using AI. It combines retrieval, summarization, and generation to support faster document drafting.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/generate-documents-from-your-data",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning'],
        products=['azure-cognitive-search', 'azure-cosmos-db', 'microsoft-foundry'],
    ),
    "intelligent_apps_image_processing": AzureArchitectureEntry(
        key="intelligent_apps_image_processing",
        name="Image classification on Azure",
        summary="Learn how to build image processing into your applications by using Azure services such as the Computer Vision API and Azure Functions.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/intelligent-apps-image-processing",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning', 'Media'],
        products=['azure-blob-storage', 'azure-computer-vision', 'azure-cosmos-db', 'azure-event-grid', 'azure-functions'],
    ),
    "measure_azure_app_sustainability_sci_score": AzureArchitectureEntry(
        key="measure_azure_app_sustainability_sci_score",
        name="Measure Azure app sustainability by using the SCI score",
        summary="Create a sustainability model based on available proxies that scores the carbon impact of an application by using the SCI score.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/apps/measure-azure-app-sustainability-sci-score",
        entry_type="Architecture",
        categories=['AI + Machine Learning', 'Databases', 'Storage'],
        products=['azure-monitor', 'azure-automation', 'azure-logic-apps', 'power-bi'],
    ),
    "ai_search_skillsets": AzureArchitectureEntry(
        key="ai_search_skillsets",
        name="Use AI enrichment with image and text processing",
        summary="Learn how to transform unstructured image and text data into full-text searchable content with Azure AI Search prebuilt skills and custom skills.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/ai-search-skillsets",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning'],
        products=['azure-app-service', 'azure-blob-storage', 'azure-cognitive-search', 'azure-functions'],
    ),
    "next_order_forecasting": AzureArchitectureEntry(
        key="next_order_forecasting",
        name="Use AI to forecast customer orders",
        summary="Learn how to use AI and machine learning to forecast a customer\'s future order quantity for a specific SKU. See the Azure services that you can use in this solution.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/next-order-forecasting",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning', 'Analytics'],
        products=['azure-machine-learning', 'fabric', 'azure-data-lake', 'azure-sql-database', 'power-apps'],
    ),
    "orchestrate_machine_learning_azure_databricks": AzureArchitectureEntry(
        key="orchestrate_machine_learning_azure_databricks",
        name="Use Azure Databricks to orchestrate MLOps",
        summary="Learn about an approach for machine learning operations (MLOps) that uses Azure Databricks to run model training and batch scoring.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/orchestrate-machine-learning-azure-databricks",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning'],
        products=['azure-databricks'],
    ),
    "many_models_machine_learning_azure_machine_learning": AzureArchitectureEntry(
        key="many_models_machine_learning_azure_machine_learning",
        name="Use the many-models architecture approach to scale machine learning models",
        summary="Learn how to manage and deploy a many-models architecture by using Azure Machine Learning and compute clusters to scale machine learning models.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/many-models-machine-learning-azure-machine-learning",
        entry_type="Solution Idea",
        categories=['AI + Machine Learning', 'Analytics'],
        products=['azure-data-factory', 'azure-data-lake', 'azure-databricks', 'azure-machine-learning', 'azure-synapse-analytics'],
    ),
    "small_medium_modern_data_platform": AzureArchitectureEntry(
        key="small_medium_modern_data_platform",
        name="Build a modern data platform architecture for SMBs by using Microsoft Fabric and Azure Databricks",
        summary="Use Microsoft Fabric and Azure Databricks to build a modern data platform architecture designed for small and medium businesses.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/small-medium-modern-data-platform",
        entry_type="Solution Idea",
        categories=['Analytics', 'Databases', 'Storage'],
        products=['azure-data-lake', 'azure-databricks', 'fabric', 'dynamics-365', 'azure-data-factory'],
    ),
    "automotive_telemetry_analytics": AzureArchitectureEntry(
        key="automotive_telemetry_analytics",
        name="Data analytics for automotive test fleets",
        summary="Learn about a data analytics solution that can democratize data access and provide R&D engineers with near real-time insights into test drive diagnostic data.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/industries/automotive/automotive-telemetry-analytics",
        entry_type="Architecture",
        categories=['Analytics', 'Internet of Things'],
        products=['fabric', 'azure-data-explorer', 'azure-event-hubs', 'azure-functions', 'azure-event-grid'],
    ),
    "data_warehouse": AzureArchitectureEntry(
        key="data_warehouse",
        name="Data warehousing and analytics",
        summary="This example demonstrates a data pipeline that integrates large amounts of data from multiple sources into a unified analytics platform in Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/data/data-warehouse",
        entry_type="Architecture",
        categories=['Analytics', 'Databases'],
        products=['azure-data-lake-storage', 'azure-cosmos-db', 'azure-data-factory', 'azure-sql-database', 'azure-table-storage'],
    ),
    "esri_arcgis_azure_virtual_desktop": AzureArchitectureEntry(
        key="esri_arcgis_azure_virtual_desktop",
        name="Deploy Esri ArcGIS Pro in Azure Virtual Desktop",
        summary="View a reference architecture that shows how to deploy ArcGIS Pro in Azure Virtual Desktop to support the hyperscale of Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/data/esri-arcgis-azure-virtual-desktop",
        entry_type="Architecture",
        categories=['Analytics', 'Virtual Desktop', 'Databases', 'Identity'],
        products=['azure-virtual-desktop', 'azure-netapp-files', 'azure-monitor', 'azure-policy', 'entra-id'],
    ),
    "call_center_openai_analytics": AzureArchitectureEntry(
        key="call_center_openai_analytics",
        name="Extract and analyze call center data",
        summary="Learn how to extract insights from customer conversations at a call center by using Foundry Tools and Azure OpenAI in Foundry Models.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/openai/architecture/call-center-openai-analytics",
        entry_type="Architecture",
        categories=['Analytics', 'AI + Machine Learning'],
        products=['azure-blob-storage', 'azure-speech', 'foundry-tools', 'power-bi'],
    ),
    "greenfield_lakehouse_fabric": AzureArchitectureEntry(
        key="greenfield_lakehouse_fabric",
        name="Greenfield lakehouse on Microsoft Fabric",
        summary="Learn about a greenfield solution for creating a robust, scalable data platform by using the lakehouse design paradigm on Microsoft Fabric.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/data/greenfield-lakehouse-fabric",
        entry_type="Reference Architecture",
        categories=['Analytics', 'Databases', 'Storage'],
        products=['fabric', 'power-bi'],
    ),
    "ingest_etl_stream_with_adb": AzureArchitectureEntry(
        key="ingest_etl_stream_with_adb",
        name="Ingestion, ETL, and stream processing pipelines with Azure Databricks and Delta Lake",
        summary="Create ETL pipelines for batch and streaming data with Azure Databricks to simplify data lake ingestion at any scale.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/ingest-etl-stream-with-adb",
        entry_type="Solution Idea",
        categories=['Analytics', 'Internet of Things', 'Databases'],
        products=['azure-databricks', 'azure-data-lake-storage', 'azure-iot-hub', 'azure-data-factory', 'azure-event-hubs'],
    ),
    "iot_azure_data_explorer": AzureArchitectureEntry(
        key="iot_azure_data_explorer",
        name="IoT analytics with Azure Data Explorer and Azure IoT Hub",
        summary="Use Azure Data Explorer for near real-time IoT telemetry analytics on fast-flowing, high-volume streaming data from a wide range of IoT devices.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/iot-azure-data-explorer",
        entry_type="Solution Idea",
        categories=['Analytics', 'Internet of Things'],
        products=['azure-cosmos-db', 'azure-data-explorer', 'azure-digital-twins', 'azure-iot-hub'],
    ),
    "fabric_deployment_patterns": AzureArchitectureEntry(
        key="fabric_deployment_patterns",
        name="Microsoft Fabric deployment patterns",
        summary="This article provides an overview of common deployment scenarios for Microsoft Fabric.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/analytics/architecture/fabric-deployment-patterns",
        entry_type="Architecture",
        categories=['Analytics'],
        products=['fabric'],
    ),
    "small_medium_data_warehouse": AzureArchitectureEntry(
        key="small_medium_data_warehouse",
        name="Modern data warehouses for small or medium-sized businesses",
        summary="Learn how to use Microsoft Fabric, Azure SQL Database, Azure SQL Managed Instance, and Azure Data Lake Storage to modernize legacy and on-premises data.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/data/small-medium-data-warehouse",
        entry_type="Architecture",
        categories=['Analytics', 'Databases', 'Storage'],
        products=['azure-data-lake', 'azure-sql-database', 'fabric'],
    ),
    "analytics_service_bus": AzureArchitectureEntry(
        key="analytics_service_bus",
        name="Real-time analytics with Azure Service Bus and Microsoft Fabric",
        summary="Learn how to use Microsoft Fabric with Azure Service Bus for near real-time solutions.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/analytics-service-bus",
        entry_type="Solution Idea",
        categories=['Analytics'],
        products=['azure-service-bus', 'real-time-analytics', 'fabric'],
    ),
    "sync_mongodb_atlas_fabric_analytics": AzureArchitectureEntry(
        key="sync_mongodb_atlas_fabric_analytics",
        name="Set up real-time sync of MongoDB Atlas data changes to Microsoft Fabric",
        summary="Learn how to integrate MongoDB Atlas with Microsoft Fabric by using open mirroring to keep data tables in sync with operational data changes.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/analytics/sync-mongodb-atlas-fabric-analytics",
        entry_type="Architecture",
        categories=['Analytics'],
        products=['fabric'],
    ),
    "stream_processing_databricks": AzureArchitectureEntry(
        key="stream_processing_databricks",
        name="Stream processing with Azure Databricks",
        summary="Create an end-to-end stream processing pipeline in Azure by using Azure Databricks.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/data/stream-processing-databricks",
        entry_type="Reference Architecture",
        categories=['Analytics', 'Databases'],
        products=['azure-cosmos-db', 'azure-databricks', 'azure-event-hubs', 'azure-log-analytics', 'azure-monitor'],
    ),
    "stream_processing_stream_analytics": AzureArchitectureEntry(
        key="stream_processing_stream_analytics",
        name="Stream processing with Azure Stream Analytics",
        summary="This reference architecture shows an end-to-end stream processing pipeline, which ingests data, correlates records, and calculates a rolling average.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/data/stream-processing-stream-analytics",
        entry_type="Reference Architecture",
        categories=['Analytics', 'Databases'],
        products=['azure-cosmos-db', 'azure-event-hubs', 'azure-monitor', 'azure-stream-analytics'],
    ),
    "real_time_lakehouse_data_processing": AzureArchitectureEntry(
        key="real_time_lakehouse_data_processing",
        name="Use Azure Synapse Analytics for near real-time lakehouse data processing",
        summary="Use Azure Event Hubs, Azure Synapse Analytics, and Azure Data Lake Storage to create an end-to-end, near real-time data lakehouse data processing solution.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/data/real-time-lakehouse-data-processing",
        entry_type="Architecture",
        categories=['Analytics'],
        products=['azure-cognitive-search', 'azure-cosmos-db', 'azure-data-lake', 'azure-event-hubs', 'azure-synapse-analytics'],
    ),
    "enterprise_bi_microsoft_fabric": AzureArchitectureEntry(
        key="enterprise_bi_microsoft_fabric",
        name="Use Microsoft Fabric to design an enterprise BI solution",
        summary="Learn how to implement a pipeline that moves data from an on-premises data warehouse into Microsoft Fabric and transforms the data for analysis.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/analytics/enterprise-bi-microsoft-fabric",
        entry_type="Architecture",
        categories=['Analytics', 'Databases', 'Integration'],
        products=['fabric', 'azure-blob-storage', 'entra-id', 'power-bi'],
    ),
    "baseline": AzureArchitectureEntry(
        key="baseline",
        name="Azure Virtual Machines baseline architecture",
        summary="Learn how to set up an environment that\'s configured to run a workload on Azure Virtual Machines.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/virtual-machines/baseline",
        entry_type="Reference Architecture",
        categories=['Compute', 'Migration', 'Networking'],
        products=['azure-bastion', 'azure-key-vault', 'azure-virtual-machines', 'azure-virtual-network', 'azure-vm-scalesets'],
    ),
    "baseline_landing_zone": AzureArchitectureEntry(
        key="baseline_landing_zone",
        name="Azure Virtual Machines baseline architecture in an Azure landing zone",
        summary="Learn how to build on the baseline architecture to address changes and expectations when you deploy it in an Azure landing zone.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/virtual-machines/baseline-landing-zone",
        entry_type="Architecture",
        categories=['Compute', 'Migration', 'Networking'],
        products=['azure-bastion', 'azure-firewall', 'azure-log-analytics', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "spot_eviction": AzureArchitectureEntry(
        key="spot_eviction",
        name="Build workloads on spot virtual machines",
        summary="Provides best practices for building workloads with Azure Spot Virtual Machines.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/spot/spot-eviction",
        entry_type="Architecture",
        categories=['Compute'],
        products=['azure-virtual-machines'],
    ),
    "deploy_ibm_maximo_application_suite": AzureArchitectureEntry(
        key="deploy_ibm_maximo_application_suite",
        name="Deploy IBM Maximo Application Suite on Azure",
        summary="Learn how to run IBM Maximo Application Suite (MAS) on Azure. See guidance for designing and implementing cloud solutions with Maximo 8.5 and up that use Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/apps/deploy-ibm-maximo-application-suite",
        entry_type="Architecture",
        categories=['Compute', 'Containers', 'Storage', 'Analytics', 'Internet of Things'],
        products=['azure-files', 'azure-load-balancer', 'azure-redhat-openshift', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "deploy_ibm_sterling_oms": AzureArchitectureEntry(
        key="deploy_ibm_sterling_oms",
        name="Deploy IBM Sterling Order Management on Azure",
        summary="Run IBM Sterling Order Management Software (OMS) on Azure. Design and implement cloud solutions for Sterling OMS that use Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/ibm/deploy-ibm-sterling-oms",
        entry_type="Architecture",
        categories=['Compute', 'Containers', 'Storage', 'Analytics'],
        products=['azure-database-postgresql', 'azure-files', 'azure-redhat-openshift', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "process_batch_transactions": AzureArchitectureEntry(
        key="process_batch_transactions",
        name="High-volume batch transaction processing",
        summary="Use Azure Kubernetes Service (AKS) and Azure Service Bus to implement high-volume batch transaction processing.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/process-batch-transactions",
        entry_type="Architecture",
        categories=['Compute', 'Hybrid + Multicloud', 'Migration'],
        products=['azure-kubernetes-service', 'azure-service-bus', 'azure-virtual-machines'],
    ),
    "event_hubs_functions": AzureArchitectureEntry(
        key="event_hubs_functions",
        name="Integrate Event Hubs with serverless functions on Azure",
        summary="Learn how to architect, develop, and deploy efficient and scalable code that runs on Azure Functions and responds to Event Hubs events.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/serverless/event-hubs-functions/event-hubs-functions",
        entry_type="Architecture",
        categories=['Compute', 'Integration'],
        products=['azure-event-hubs', 'azure-functions', 'azure-monitor'],
    ),
    "virtual_machine_compliance": AzureArchitectureEntry(
        key="virtual_machine_compliance",
        name="Manage virtual machine compliance",
        summary="Manage virtual machine compliance without impairing DevOps practices. Use Azure VM Image Builder and Azure Compute Gallery to minimize risk from system images.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/security/virtual-machine-compliance",
        entry_type="Architecture",
        categories=['Compute', 'DevOps', 'Management + Governance', 'Security'],
        products=['azure-policy'],
    ),
    "observability": AzureArchitectureEntry(
        key="observability",
        name="Monitor Azure Functions and Event Hubs",
        summary="Learn how to monitor an Azure Functions topology that uses Event Hubs.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/serverless/event-hubs-functions/observability",
        entry_type="Architecture",
        categories=['Compute', 'Integration'],
        products=['azure-event-hubs', 'azure-functions', 'azure-monitor'],
    ),
    "performance_scale": AzureArchitectureEntry(
        key="performance_scale",
        name="Performance and scale guidance for Event Hubs and Azure Functions",
        summary="Learn how to plan for and deploy more efficient and scalable code that runs on Azure Functions and responds to Event Hubs events.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/serverless/event-hubs-functions/performance-scale",
        entry_type="Architecture",
        categories=['Compute', 'Integration'],
        products=['azure-event-hubs', 'azure-functions'],
    ),
    "quantum_computing_integration_with_classical_apps": AzureArchitectureEntry(
        key="quantum_computing_integration_with_classical_apps",
        name="Quantum computing integration with classical apps",
        summary="Learn how to use Azure Quantum to implement hybrid quantum applications.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/quantum/quantum-computing-integration-with-classical-apps",
        entry_type="Architecture",
        categories=['Compute', 'Hybrid + Multicloud'],
        products=['azure-quantum', 'azure-key-vault', 'entra-id'],
    ),
    "linux_vm": AzureArchitectureEntry(
        key="linux_vm",
        name="Run a Linux VM on Azure",
        summary="Learn the best practices for running a Linux virtual machine on Azure, which requires some additional components, including networking and storage resources.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/n-tier/linux-vm",
        entry_type="Reference Architecture",
        categories=['Compute'],
        products=['azure-backup', 'azure-blob-storage', 'azure-storage', 'azure-virtual-machines'],
    ),
    "windows_vm": AzureArchitectureEntry(
        key="windows_vm",
        name="Run a Windows VM on Azure",
        summary="Learn the best practices for running a Windows virtual machine on Azure, which requires some additional components, including networking and storage resources.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/n-tier/windows-vm",
        entry_type="Architecture",
        categories=['Compute'],
        products=['azure-backup', 'azure-blob-storage', 'azure-resource-manager', 'azure-storage', 'azure-virtual-machines'],
    ),
    "sas_overview": AzureArchitectureEntry(
        key="sas_overview",
        name="SAS on Azure architecture",
        summary="Learn how to run SAS analytics products on Azure. See guidelines for designing and implementing cloud solutions for SAS Viya and SAS Grid that use Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/sas/sas-overview",
        entry_type="Architecture",
        categories=['Compute', 'Storage', 'Analytics'],
        products=['azure-virtual-machines', 'azure-virtual-network', 'azure-files'],
    ),
    "unisys_clearpath_forward_mainframe_rehost": AzureArchitectureEntry(
        key="unisys_clearpath_forward_mainframe_rehost",
        name="Unisys ClearPath MCP virtualization on Azure",
        summary="Learn how to apply Unisys virtualization technologies to migrate a legacy Unisys ClearPath Forward Libra mainframe to Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/unisys-clearpath-forward-mainframe-rehost",
        entry_type="Architecture",
        categories=['Compute', 'Hybrid + Multicloud', 'Migration'],
        products=['azure-expressroute', 'azure-storage', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "aks_multi_cluster": AzureArchitectureEntry(
        key="aks_multi_cluster",
        name="AKS baseline for multiregion clusters",
        summary="A design for baseline infrastructure that deploys an Azure Kubernetes Service (AKS) cluster to multiple regions.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-multi-region/aks-multi-cluster",
        entry_type="Architecture",
        categories=['Containers'],
        products=['azure-kubernetes-service', 'azure-front-door', 'azure-application-gateway', 'azure-container-registry', 'azure-firewall'],
    ),
    "access_azure_kubernetes_service_cluster_api_server": AzureArchitectureEntry(
        key="access_azure_kubernetes_service_cluster_api_server",
        name="Access an Azure Kubernetes Service (AKS) API server",
        summary="Learn more about how to connect to an Azure Kubernetes Service (AKS) cluster\'s API server. Possibilities include Azure Bastion, ExpressRoute, and Cloud Shell.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/security/access-azure-kubernetes-service-cluster-api-server",
        entry_type="Architecture",
        categories=['Containers', 'Security'],
        products=['azure-bastion', 'azure-expressroute', 'azure-kubernetes-service', 'azure-private-link', 'azure-vpn-gateway'],
    ),
    "aks_microservices_advanced": AzureArchitectureEntry(
        key="aks_microservices_advanced",
        name="Advanced Azure Kubernetes Service (AKS) microservices architecture",
        summary="Learn about a scalable, secure AKS microservices architecture that builds on recommended AKS microservices baseline architectures and implementations.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices-advanced",
        entry_type="Reference Architecture",
        categories=['Containers'],
        products=['azure-application-gateway', 'azure-container-registry', 'azure-kubernetes-service', 'azure-virtual-network'],
    ),
    "baseline_aks": AzureArchitectureEntry(
        key="baseline_aks",
        name="Baseline architecture for an Azure Kubernetes Service (AKS) cluster",
        summary="Reference architecture for a baseline infrastructure that deploys an Azure Kubernetes Service (AKS) cluster.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks/baseline-aks",
        entry_type="Reference Architecture",
        categories=['Containers'],
        products=['azure-application-gateway', 'azure-container-registry', 'azure-firewall', 'azure-kubernetes-service', 'azure-rbac'],
    ),
    "blue_green_deployment_for_aks": AzureArchitectureEntry(
        key="blue_green_deployment_for_aks",
        name="Blue-green deployment of AKS clusters",
        summary="Learn how to deploy AKS clusters using a blue-green strategy.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/aks/blue-green-deployment-for-aks",
        entry_type="Architecture",
        categories=['Containers', 'DevOps', 'Management + Governance'],
        products=['azure-kubernetes-service', 'azure-application-gateway', 'azure-container-registry', 'azure-front-door', 'azure-dns'],
    ),
    "ci_cd_kubernetes": AzureArchitectureEntry(
        key="ci_cd_kubernetes",
        name="Build a CI/CD pipeline for microservices on Kubernetes with Azure DevOps and Helm",
        summary="Learn about building a continuous integration and continuous delivery (CI/CD) pipeline for deploying microservices to Azure Kubernetes Service (AKS) with Azure DevOps and Helm.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/microservices/ci-cd-kubernetes",
        entry_type="Architecture",
        categories=['Containers'],
        products=['azure-kubernetes-service', 'azure-container-registry', 'azure-devops'],
    ),
    "aks_hybrid_azure_local": AzureArchitectureEntry(
        key="aks_hybrid_azure_local",
        name="Deploy and operate apps with AKS enabled by Azure Arc on Azure Local",
        summary="Build containerized app deployment pipelines for AKS on Azure Local with Azure Arc and GitOps. Learn about Flux automation for hybrid Kubernetes clusters.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/hybrid/aks-hybrid-azure-local",
        entry_type="Architecture",
        categories=['Containers', 'Hybrid + Multicloud'],
        products=['azure-kubernetes-service', 'azure-local', 'azure-arc', 'github', 'azure-pipelines'],
    ),
    "microservices_with_container_apps_dapr": AzureArchitectureEntry(
        key="microservices_with_container_apps_dapr",
        name="Deploy microservices with Azure Container Apps and Dapr",
        summary="Build a serverless microservices solution on Azure Container Apps by using Distributed Application Runtime (Dapr) and Kubernetes event-driven autoscaling (KEDA).",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/serverless/microservices-with-container-apps-dapr",
        entry_type="Architecture",
        categories=['Containers', 'Web'],
        products=['azure-container-apps', 'dotnet', 'azure-sql-database', 'azure-cosmos-db', 'azure-managed-redis'],
    ),
    "gitops_blueprint_aks": AzureArchitectureEntry(
        key="gitops_blueprint_aks",
        name="GitOps for Azure Kubernetes Service",
        summary="Learn techniques for using GitOps principles to operate and manage an Azure Kubernetes Services (AKS) cluster. The solutions use Flux v2 and Argo CD.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/gitops-aks/gitops-blueprint-aks",
        entry_type="Architecture",
        categories=['Containers', 'DevOps'],
        products=['azure-kubernetes-service', 'github'],
    ),
    "aks_high_availability": AzureArchitectureEntry(
        key="aks_high_availability",
        name="High availability for multitier AKS applications",
        summary="High availability for multitier application deployment in AKS clusters, including a checklist to identify and eliminate points of failure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/aks/aks-high-availability",
        entry_type="Architecture",
        categories=['Containers'],
        products=['azure-cosmos-db', 'azure-disk-storage', 'azure-files', 'azure-kubernetes-service', 'azure-load-balancer'],
    ),
    "sma_opcon_azure": AzureArchitectureEntry(
        key="sma_opcon_azure",
        name="Implement an SMA OpCon environment in Azure",
        summary="Learn how to use SMA Technologies OpCon in a Kubernetes configuration to automate Azure and on-premises workloads that run on various servers across an enterprise.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/integration/sma-opcon-azure",
        entry_type="Architecture",
        categories=['Containers', 'Hybrid + Multicloud'],
        products=['azure-kubernetes-service', 'azure-private-link', 'azure-sql-database', 'azure-storage', 'azure-vpn-gateway'],
    ),
    "aks_microservices": AzureArchitectureEntry(
        key="aks_microservices",
        name="Microservices architecture on Azure Kubernetes Service",
        summary="Learn about the infrastructure and DevOps considerations to deploy and run a microservices architecture on Azure Kubernetes Service (AKS).",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices",
        entry_type="Reference Architecture",
        categories=['Containers'],
        products=['entra-id', 'azure-container-registry', 'azure-kubernetes-service', 'azure-managed-redis', 'azure-pipelines'],
    ),
    "mission_critical_intro": AzureArchitectureEntry(
        key="mission_critical_intro",
        name="Mission-critical architecture on Azure",
        summary="Architecture design for a highly reliable workload.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-mission-critical/mission-critical-intro",
        entry_type="Architecture",
        categories=['Containers', 'Networking', 'Security', 'DevOps'],
        products=['azure-front-door', 'azure-container-registry', 'azure-kubernetes-service', 'azure-rbac'],
    ),
    "aks_firewall": AzureArchitectureEntry(
        key="aks_firewall",
        name="Use Azure Firewall to help protect an Azure Kubernetes Service (AKS) cluster",
        summary="Learn how to deploy an Azure Kubernetes Service (AKS) cluster in a hub-and-spoke network topology by using Terraform and Azure DevOps. Help protect inbound and outbound traffic by using Azure Firew...",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/aks/aks-firewall",
        entry_type="Architecture",
        categories=['Containers', 'Security', 'Networking'],
        products=[],
    ),
    "aks_front_door": AzureArchitectureEntry(
        key="aks_front_door",
        name="Use Azure Front Door to secure AKS workloads",
        summary="Learn how to secure AKS workloads by using end-to-end TLS encryption, Azure Front Door Premium, an Azure Private Link service, and the NGINX ingress controller.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/aks-front-door/aks-front-door",
        entry_type="Architecture",
        categories=['Containers', 'Networking'],
        products=['azure-front-door', 'azure-key-vault', 'azure-private-link', 'azure-container-registry', 'azure-kubernetes-service'],
    ),
    "azure_redhat_openshift_financial_services_workloads": AzureArchitectureEntry(
        key="azure_redhat_openshift_financial_services_workloads",
        name="Use Azure Red Hat OpenShift in the financial services industry",
        summary="Learn how to use an Azure Red Hat OpenShift landing zone for the financial services industry to create secure, resilient, and compliant solutions in a hybrid cloud environment.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aro/azure-redhat-openshift-financial-services-workloads",
        entry_type="Architecture",
        categories=['Containers', 'Hybrid + Multicloud', 'Security'],
        products=['azure-redhat-openshift'],
    ),
    "aks_agic": AzureArchitectureEntry(
        key="aks_agic",
        name="Use the Application Gateway Ingress Controller with a multitenant Azure Kubernetes Service cluster",
        summary="Learn how to use the Application Gateway Ingress Controller (AGIC) with your AKS cluster to expose microservice-based applications to the internet.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/aks-agic/aks-agic",
        entry_type="Architecture",
        categories=['Containers', 'Networking'],
        products=['azure-application-gateway', 'azure-key-vault', 'azure-container-registry', 'azure-kubernetes-service', 'azure-bastion'],
    ),
    "data_platform_end_to_end": AzureArchitectureEntry(
        key="data_platform_end_to_end",
        name="Analytics end-to-end with Microsoft Fabric",
        summary="This example scenario demonstrates how to use the family of Microsoft data services to build a modern analytics platform capable of handling the most common data challenges in an organization.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/dataplate2e/data-platform-end-to-end",
        entry_type="Architecture",
        categories=['Databases', 'Analytics'],
        products=['fabric', 'azure-cosmos-db', 'real-time-analytics', 'azure-databricks', 'azure-event-hubs'],
    ),
    "azure_data_factory_on_azure_landing_zones_baseline": AzureArchitectureEntry(
        key="azure_data_factory_on_azure_landing_zones_baseline",
        name="Azure Data Factory baseline architecture in an Azure landing zone",
        summary="Learn how to design and implement the medallion lakehouse architecture in an Azure landing zone by using Azure Data Factory, Azure Databricks, SQL Server, and Power BI.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/architecture/azure-data-factory-on-azure-landing-zones-baseline",
        entry_type="Reference Architecture",
        categories=['Databases', 'Storage', 'Networking', 'Security'],
        products=['azure-data-factory', 'azure-key-vault', 'azure-databricks', 'azure-sql-database'],
    ),
    "azure_data_factory_enterprise_hardened": AzureArchitectureEntry(
        key="azure_data_factory_enterprise_hardened",
        name="Azure Data Factory enterprise hardened architecture",
        summary="Learn how to design an enterprise-hardened workload for Azure Data Factory in an Azure landing zone to build robust and efficient data pipelines.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/architecture/azure-data-factory-enterprise-hardened",
        entry_type="Architecture",
        categories=['Databases', 'Storage', 'Networking', 'Security'],
        products=['azure-data-factory', 'azure-key-vault', 'azure-databricks', 'azure-sql-database'],
    ),
    "azure_data_factory_mission_critical": AzureArchitectureEntry(
        key="azure_data_factory_mission_critical",
        name="Azure Data Factory mission-critical architecture",
        summary="Learn how to design a mission-critical workload for Azure Data Factory in an Azure landing zone to build robust and efficient data pipelines.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/architecture/azure-data-factory-mission-critical",
        entry_type="Architecture",
        categories=['Databases', 'Storage', 'Networking', 'Security'],
        products=['azure-data-factory', 'azure-key-vault', 'azure-databricks', 'azure-sql-database', 'azure-container-apps'],
    ),
    "caching": AzureArchitectureEntry(
        key="caching",
        name="Caching guidance",
        summary="Learn how caching can improve the performance and scalability of a system by copying frequently accessed data to fast storage close to the application.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching",
        entry_type="Architecture",
        categories=['Databases', 'Identity', 'Web', 'Storage', 'Security'],
        products=['azure-managed-redis'],
    ),
    "search_blob_metadata": AzureArchitectureEntry(
        key="search_blob_metadata",
        name="Create an Azure AI Search index based on file content and metadata",
        summary="Build an Azure AI Search index to search for documents by using file content from Azure Blob Storage and metadata from Azure Table Storage.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/search-blob-metadata",
        entry_type="Architecture",
        categories=['Databases', 'AI + Machine Learning', 'Storage'],
        products=['azure-cognitive-search', 'azure-blob-storage', 'azure-table-storage'],
    ),
    "secure_sql_managed_instance_managed_hardware_security_module": AzureArchitectureEntry(
        key="secure_sql_managed_instance_managed_hardware_security_module",
        name="Cross-region resiliency for SQL TDE with Azure Key Vault Managed HSM",
        summary="This solution describes a secure and resilient deployment pattern for Azure SQL Managed Instance. It highlights how Azure Key Vault Managed HSM stores customer-managed TDE protector keys.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/secure-sql-managed-instance-managed-hardware-security-module",
        entry_type="Solution Idea",
        categories=['Databases', 'Security'],
        products=['azure-sql-managed-instance', 'azure-key-vault'],
    ),
    "data_streaming_scenario": AzureArchitectureEntry(
        key="data_streaming_scenario",
        name="Data streaming with AKS",
        summary="Use AKS to easily ingest and process a real-time data stream, with millions of data points collected via sensors.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/data-streaming-scenario",
        entry_type="Solution Idea",
        categories=['Databases'],
        products=['azure-app-service', 'azure-api-management', 'azure-container-registry', 'azure-managed-redis', 'azure-cosmos-db'],
    ),
    "dataops_mdw": AzureArchitectureEntry(
        key="dataops_mdw",
        name="DataOps for the modern data warehouse",
        summary="How to apply DevOps principles to data pipelines built according to the modern data warehouse (MDW) architectural pattern with Microsoft Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/architecture/dataops-mdw",
        entry_type="Architecture",
        categories=['Databases'],
        products=['azure-data-factory', 'azure-databricks', 'azure-devops', 'azure-key-vault', 'azure-synapse-analytics'],
    ),
    "azure_data_factory_on_azure_landing_zones_index": AzureArchitectureEntry(
        key="azure_data_factory_on_azure_landing_zones_index",
        name="Design a medallion lakehouse with Azure Data Factory",
        summary="Learn how to design and implement the medallion lakehouse architecture in an Azure landing zone by using Azure Data Factory, Azure Databricks, Azure SQL Server, and Power BI.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/architecture/azure-data-factory-on-azure-landing-zones-index",
        entry_type="Architecture",
        categories=['Databases', 'Storage', 'Networking', 'Security'],
        products=['azure-data-factory'],
    ),
    "topic_migrate_oracle_azure": AzureArchitectureEntry(
        key="topic_migrate_oracle_azure",
        name="Migrate an Oracle database to Azure",
        summary="Learn how to migrate an Oracle database and its applications to Azure. You can migrate to either Azure virtual machines or OD@A Exadata Database Service.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/idea/topic-migrate-oracle-azure",
        entry_type="Solution Idea",
        categories=['Databases', 'Migration'],
        products=['azure-virtual-machines', 'azure-expressroute', 'azure-vpn-gateway'],
    ),
    "migrate_oracle_odaa_exadata": AzureArchitectureEntry(
        key="migrate_oracle_odaa_exadata",
        name="Migrate an Oracle database to OD@A Exadata Database Service",
        summary="Learn how to use Oracle ZDM and Azure networking to migrate an Oracle database to Oracle Database@Azure Exadata Database Service.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/idea/migrate-oracle-odaa-exadata",
        entry_type="Solution Idea",
        categories=['Databases', 'Migration'],
        products=['azure-expressroute', 'azure-vpn-gateway'],
    ),
    "migrate_oracle_azure_iaas": AzureArchitectureEntry(
        key="migrate_oracle_azure_iaas",
        name="Migrate an Oracle database to an Azure virtual machine",
        summary="Learn how to migrate an Oracle database to an Azure virtual machine by using Oracle Data Guard and Azure networking.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/idea/migrate-oracle-azure-iaas",
        entry_type="Solution Idea",
        categories=['Databases', 'Migration'],
        products=['azure-virtual-machines', 'azure-expressroute', 'azure-vpn-gateway'],
    ),
    "mainframe_data_replication_azure_data_platform": AzureArchitectureEntry(
        key="mainframe_data_replication_azure_data_platform",
        name="Migrate mainframe data tier to Azure with mLogica LIBER*IRIS",
        summary="Find out how mLogica LIBER*IRIS provides a proven solution for bulk data migration from a mainframe to Azure for enterprise workloads.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/mainframe-data-replication-azure-data-platform",
        entry_type="Architecture",
        categories=['Databases', 'DevOps', 'Migration', 'Storage'],
        products=['azure-database-mysql', 'azure-database-postgresql', 'azure-cosmos-db', 'azure-sql-database', 'azure-storage'],
    ),
    "minimal_storage_change_feed_replicate_data": AzureArchitectureEntry(
        key="minimal_storage_change_feed_replicate_data",
        name="Minimal storage – change feed to replicate data",
        summary="Architecture for a high-availability solution that uses two Azure storage services, one for quick access to high-demand data, the other for low-demand data.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/databases/idea/minimal-storage-change-feed-replicate-data",
        entry_type="Solution Idea",
        categories=['Databases', 'Web', 'Migration', 'Storage'],
        products=['azure-front-door', 'azure-app-service', 'azure-functions', 'azure-cosmos-db', 'azure-table-storage'],
    ),
    "moodle_azure_netapp_files": AzureArchitectureEntry(
        key="moodle_azure_netapp_files",
        name="Moodle deployment with Azure NetApp Files",
        summary="Deploy Moodle with Azure NetApp Files for a resilient solution that provides high-throughput, low-latency access to scalable shared storage.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/file-storage/moodle-azure-netapp-files",
        entry_type="Architecture",
        categories=['Databases', 'Networking', 'Storage'],
        products=['azure-application-gateway', 'azure-managed-redis', 'azure-database-mysql', 'azure-netapp-files', 'azure-vm-scalesets'],
    ),
    "oracle_azure_netapp_files": AzureArchitectureEntry(
        key="oracle_azure_netapp_files",
        name="Oracle Database with Azure NetApp Files",
        summary="Implement a high-bandwidth, low-latency solution for Oracle Database workloads. Use Azure NetApp Files for enterprise-scale performance and reduced costs.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/file-storage/oracle-azure-netapp-files",
        entry_type="Architecture",
        categories=['Databases', 'Hybrid + Multicloud', 'Migration', 'Networking', 'Storage'],
        products=['azure-netapp-files', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "run_sap_bw4hana_with_linux_virtual_machines": AzureArchitectureEntry(
        key="run_sap_bw4hana_with_linux_virtual_machines",
        name="Run SAP BW/4HANA with Linux virtual machines on Azure",
        summary="Learn about the SAP BW/4HANA application tier and how it\'s suitable for a small-scale production environment of SAP BW/4HANA on Azure where high availability is a priority.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/sap/run-sap-bw4hana-with-linux-virtual-machines",
        entry_type="Reference Architecture",
        categories=['Databases', 'Compute'],
        products=['azure-bastion', 'azure-managed-disks', 'azure-virtual-machines', 'azure-virtual-network', 'azure-sap'],
    ),
    "run_sap_hana_for_linux_virtual_machines": AzureArchitectureEntry(
        key="run_sap_hana_for_linux_virtual_machines",
        name="Run SAP HANA for Linux virtual machines in a scale-up architecture on Azure",
        summary="\'Proven practices for running SAP HANA in a high-availability, scale-up environment that supports disaster recovery on Azure.\'",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/sap/run-sap-hana-for-linux-virtual-machines",
        entry_type="Reference Architecture",
        categories=['Databases', 'Compute'],
        products=['azure', 'azure-virtual-machines'],
    ),
    "sap_production": AzureArchitectureEntry(
        key="sap_production",
        name="SAP deployment on Azure using an Oracle database",
        summary="Learn proven practices for running SAP on Oracle in Azure, with high availability.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/apps/sap-production",
        entry_type="Architecture",
        categories=['Databases'],
        products=['azure-expressroute', 'azure-sap', 'azure-virtual-machines', 'azure-virtual-network', 'azure-netapp-files'],
    ),
    "sql_server_azure_netapp_files": AzureArchitectureEntry(
        key="sql_server_azure_netapp_files",
        name="SQL Server on Azure Virtual Machines with Azure NetApp Files",
        summary="Learn how to implement a high-bandwidth, low-latency solution for SQL Server workloads. Use Azure NetApp Files for enterprise-scale performance and reduced costs.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/file-storage/sql-server-azure-netapp-files",
        entry_type="Architecture",
        categories=['Databases', 'Hybrid + Multicloud', 'Migration', 'Networking', 'Storage'],
        products=['azure-netapp-files', 'azure-sqlserver-vm', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "virtualization_of_unisys_clearpath_forward_os_2200_enterprise_server_on_azure": AzureArchitectureEntry(
        key="virtualization_of_unisys_clearpath_forward_os_2200_enterprise_server_on_azure",
        name="Unisys ClearPath Forward OS 2200 enterprise server virtualization on Azure",
        summary="Learn how to use virtualization technologies from Microsoft partner Unisys with an existing Unisys ClearPath Forward (CPF) Dorado enterprise server.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/mainframe/virtualization-of-unisys-clearpath-forward-os-2200-enterprise-server-on-azure",
        entry_type="Architecture",
        categories=['Databases', 'Migration'],
        products=['azure-virtual-machines', 'azure-virtual-network', 'azure-expressroute'],
    ),
    "automated_api_deployments_apiops": AzureArchitectureEntry(
        key="automated_api_deployments_apiops",
        name="Automate API deployments with APIOps",
        summary="Use APIOps with an API Management instance to build and deploy APIs. This solution provides self-service tools, auditing, policy enforcement, and early feedback.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/devops/automated-api-deployments-apiops",
        entry_type="Architecture",
        categories=['DevOps', 'Developer Tools', 'Management + Governance'],
        products=['azure-api-management', 'azure-devops', 'azure-pipelines', 'github'],
    ),
    "ci_cd": AzureArchitectureEntry(
        key="ci_cd",
        name="CI/CD for microservices architectures",
        summary="Learn about continuous integration and continuous delivery for microservices, including challenges and recommended approaches.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/microservices/ci-cd",
        entry_type="Architecture",
        categories=['DevOps'],
        products=['azure'],
    ),
    "devsecops_infrastructure_as_code": AzureArchitectureEntry(
        key="devsecops_infrastructure_as_code",
        name="DevSecOps for infrastructure as code (IaC)",
        summary="Learn how to use DevSecOps for IaC to more securely and efficiently deploy cloud infrastructure into a new Azure landing zone.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/devsecops-infrastructure-as-code",
        entry_type="Solution Idea",
        categories=['DevOps', 'Security'],
        products=['microsoft-sentinel', 'azure-monitor', 'github'],
    ),
    "devsecops_on_aks": AzureArchitectureEntry(
        key="devsecops_on_aks",
        name="DevSecOps on Azure Kubernetes Service (AKS)",
        summary="DevSecOps involves utilizing security best practices from the beginning of development. These practices shift the focus on security away from auditing at the end and towards development in the begi...",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/devsecops/devsecops-on-aks",
        entry_type="Architecture",
        categories=['DevOps', 'Hybrid + Multicloud'],
        products=['azure-boards', 'azure-devops', 'azure-monitor', 'azure-pipelines', 'azure-policy'],
    ),
    "azure_governance_visualizer_accelerator": AzureArchitectureEntry(
        key="azure_governance_visualizer_accelerator",
        name="Use the Azure Governance Visualizer to optimize cloud governance",
        summary="Analyze and streamline cloud governance for compliance and operational insights by using the Azure Governance Visualizer.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/landing-zones/azure-governance-visualizer-accelerator",
        entry_type="Architecture",
        categories=['DevOps', 'Management + Governance'],
        products=['azure-app-service', 'github', 'azure-policy'],
    ),
    "sap_workload_automation_suse": AzureArchitectureEntry(
        key="sap_workload_automation_suse",
        name="Automate SAP workloads by using SUSE on Azure",
        summary="The SUSE SAP automation solution speeds deployment of SAP infrastructure on Azure. Use it to bolster productivity and facilitate innovation.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/sap-workload-automation-suse",
        entry_type="Solution Idea",
        categories=['Developer Tools', 'Migration'],
        products=['azure-files', 'azure-cloud-shell', 'azure-load-balancer', 'azure-virtual-network'],
    ),
    "app_gateway_internal_api_management_function": AzureArchitectureEntry(
        key="app_gateway_internal_api_management_function",
        name="Azure API Management landing zone architecture",
        summary="Learn about a secure enterprise API management architecture that uses Azure Application Gateway, API Management, and CI/CD pipeline deployment.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/integration/app-gateway-internal-api-management-function",
        entry_type="Architecture",
        categories=['Developer Tools', 'Integration'],
        products=['azure-api-management', 'azure-application-gateway', 'azure-functions', 'dotnet'],
    ),
    "microservices_with_container_apps": AzureArchitectureEntry(
        key="microservices_with_container_apps",
        name="Deploy Microservices to Azure Container Apps",
        summary="Deploy existing microservice applications with Azure Container Apps.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/serverless/microservices-with-container-apps",
        entry_type="Architecture",
        categories=['Developer Tools', 'Containers'],
        products=['azure-container-apps', 'azure-cosmos-db', 'azure-service-bus'],
    ),
    "reengineer_mainframe_batch_apps_azure": AzureArchitectureEntry(
        key="reengineer_mainframe_batch_apps_azure",
        name="Re-engineer mainframe batch applications on Azure",
        summary="Learn how to re-engineer mainframe batch applications to use Azure services. This architecture change can help manage increased resource cost.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/reengineer-mainframe-batch-apps-azure",
        entry_type="Architecture",
        categories=['Developer Tools', 'Migration'],
        products=['azure-data-factory', 'azure-databricks', 'azure-kubernetes-service', 'azure-sql-database', 'azure-storage'],
    ),
    "adds_forest": AzureArchitectureEntry(
        key="adds_forest",
        name="Create an Active Directory Domain Service resource forest in Azure",
        summary="Learn how to create a separate Active Directory domain in Azure that domains in your on-premises Active Directory forest trust.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/identity/adds-forest",
        entry_type="Reference Architecture",
        categories=['Identity', 'Hybrid + Multicloud'],
        products=['entra-id', 'entra', 'azure-expressroute', 'azure-virtual-network', 'azure-vpn-gateway'],
    ),
    "adds_extend_domain": AzureArchitectureEntry(
        key="adds_extend_domain",
        name="Deploy AD DS in an Azure virtual network",
        summary="Learn how to extend an on-premises Active Directory domain to Azure to provide distributed authentication services in hybrid cloud environments.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/identity/adds-extend-domain",
        entry_type="Architecture",
        categories=['Identity', 'Hybrid + Multicloud'],
        products=['entra', 'azure-virtual-network'],
    ),
    "aws_azure_ad_security": AzureArchitectureEntry(
        key="aws_azure_ad_security",
        name="Microsoft Entra identity management and access management for AWS",
        summary="Learn how Microsoft Entra ID can help secure and protect Amazon Web Services (AWS) identity management and account access. Discover Microsoft security solutions.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/aws/aws-azure-ad-security",
        entry_type="Reference Architecture",
        categories=['Identity'],
        products=['azure', 'entra-id'],
    ),
    "basic_enterprise_integration": AzureArchitectureEntry(
        key="basic_enterprise_integration",
        name="Basic enterprise integration on Azure",
        summary="Recommended architecture for implementing a simple enterprise integration pattern using Azure Logic Apps and Azure API Management.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/enterprise-integration/basic-enterprise-integration",
        entry_type="Reference Architecture",
        categories=['Integration', 'Developer Tools', 'Management + Governance'],
        products=['entra-id', 'azure-api-management', 'azure-dns', 'azure-logic-apps', 'azure-monitor'],
    ),
    "azure_security_build_first_layer_defense": AzureArchitectureEntry(
        key="azure_security_build_first_layer_defense",
        name="Build the first layer of defense with Azure Security services",
        summary="Secure your IT environment by using Azure security services and Azure Security Benchmark. This article is part of a series.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/azure-security-build-first-layer-defense",
        entry_type="Solution Idea",
        categories=['Integration', 'Security'],
        products=['azure', 'entra-id'],
    ),
    "microsoft_365_defender_build_second_layer_defense": AzureArchitectureEntry(
        key="microsoft_365_defender_build_second_layer_defense",
        name="Build the second layer of defense with Microsoft Defender XDR Security services",
        summary="Add additional security to your IT environment by using Microsoft 365 security service in addition to Azure security. This article is part of a series.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/microsoft-365-defender-build-second-layer-defense",
        entry_type="Solution Idea",
        categories=['Integration', 'Security'],
        products=['defender-office365', 'defender-for-cloud-apps', 'defender-identity', 'm365', 'mem'],
    ),
    "interservice_communication": AzureArchitectureEntry(
        key="interservice_communication",
        name="Design interservice communication for microservices",
        summary="Learn about the tradeoffs between asynchronous messaging versus synchronous APIs for communication between microservices and some challenges in communication.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/microservices/design/interservice-communication",
        entry_type="Architecture",
        categories=['Integration', 'Developer Tools'],
        products=['azure-devops'],
    ),
    "extend_mainframes_rest_apis": AzureArchitectureEntry(
        key="extend_mainframes_rest_apis",
        name="Extend mainframes to digital channels by using standards-based REST APIs",
        summary="Learn how the digital transformation architecture extends mainframe applications to Azure without disruptions or modifications to existing applications.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/extend-mainframes-rest-apis",
        entry_type="Architecture",
        categories=['Integration'],
        products=['entra-id', 'azure-expressroute', 'azure-monitor', 'azure-redhat-openshift', 'power-apps'],
    ),
    "microservice_boundaries": AzureArchitectureEntry(
        key="microservice_boundaries",
        name="Identify microservice boundaries",
        summary="Learn how to start from a carefully designed domain model to determine the right size for a microservice.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/microservices/model/microservice-boundaries",
        entry_type="Architecture",
        categories=['Integration', 'Developer Tools'],
        products=['azure-devops'],
    ),
    "microsoft_365_defender_security_integrate_azure": AzureArchitectureEntry(
        key="microsoft_365_defender_security_integrate_azure",
        name="Integrate Azure and Microsoft Defender XDR security services",
        summary="Integrate security solutions from Azure and Microsoft 365 to create robust security for your hybrid and cloud IT environments. This article is part of a series.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/microsoft-365-defender-security-integrate-azure",
        entry_type="Solution Idea",
        categories=['Integration', 'Security'],
        products=['microsoft-sentinel', 'azure-monitor', 'defender-for-cloud', 'azure-log-analytics', 'azure-network-watcher'],
    ),
    "map_threats_it_environment": AzureArchitectureEntry(
        key="map_threats_it_environment",
        name="Map threats to your IT environment",
        summary="Diagram the IT environment of your organization and develop a threat map to plan and build your defensive layer of security. This article is part of a series.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/map-threats-it-environment",
        entry_type="Solution Idea",
        categories=['Integration', 'Security'],
        products=['azure', 'office-365'],
    ),
    "raincode_reference_architecture": AzureArchitectureEntry(
        key="raincode_reference_architecture",
        name="Rehost mainframe applications to Azure with Raincode compilers",
        summary="This architecture shows how the Raincode COBOL compiler modernizes mainframe legacy applications.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/app-modernization/raincode-reference-architecture",
        entry_type="Reference Architecture",
        categories=['Integration', 'Databases'],
        products=['azure-virtual-machines', 'azure-kubernetes-service', 'azure-files', 'azure-expressroute', 'azure-load-balancer'],
    ),
    "queues_events": AzureArchitectureEntry(
        key="queues_events",
        name="Use a message broker and events to integrate enterprise systems",
        summary="Learn how to integrate enterprise back-end systems by using a message broker and events to decouple services for greater scalability and reliability.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/integration/queues-events",
        entry_type="Architecture",
        categories=['Integration', 'Developer Tools'],
        products=['azure-event-grid', 'azure-service-bus'],
    ),
    "machine_learning_inference_iot_edge": AzureArchitectureEntry(
        key="machine_learning_inference_iot_edge",
        name="Enable machine learning inference on an Azure IoT Edge device",
        summary="Enable machine learning inference on an IoT Edge device.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/iot/machine-learning-inference-iot-edge",
        entry_type="Architecture",
        categories=['Internet of Things', 'AI + Machine Learning'],
        products=['azure-iot-edge', 'azure-iot-hub'],
    ),
    "iot_move_to_production": AzureArchitectureEntry(
        key="iot_move_to_production",
        name="Move an IoT Hub-based solution from test to production",
        summary="Learn best practices for moving an IoT Hub-based solution to production, including deployment stamps, transient fault handling, and zero-touch provisioning.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/iot/iot-move-to-production",
        entry_type="Architecture",
        categories=['Internet of Things'],
        products=['azure-iot-hub'],
    ),
    "iot_private_file_upload": AzureArchitectureEntry(
        key="iot_private_file_upload",
        name="Use Azure IoT Hub to privately upload files to an Azure Storage account",
        summary="Learn how to use the Azure IoT Hub file upload feature to privately upload files to an Azure Storage account that\'s exposed through a Firewall and custom domain.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/iot/iot-private-file-upload",
        entry_type="Solution Idea",
        categories=['Internet of Things'],
        products=['azure-iot-hub', 'azure-storage', 'azure-firewall', 'azure-virtual-network', 'azure-application-gateway'],
    ),
    "automate_pdf_forms_processing": AzureArchitectureEntry(
        key="automate_pdf_forms_processing",
        name="Automate PDF forms processing",
        summary="Use Azure services such as AI Document Intelligence, Azure Logic Apps, and Azure Functions to implement cost-effective and flexible automated PDF processing.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/automate-pdf-forms-processing",
        entry_type="Architecture",
        categories=['Media'],
        products=['document-intelligence', 'foundry-tools', 'azure-logic-apps', 'azure-functions'],
    ),
    "monitoring_observable_systems_media": AzureArchitectureEntry(
        key="monitoring_observable_systems_media",
        name="Build real-time monitoring and observable systems for media",
        summary="Learn how to build scalable real-time monitoring architecture for media streaming by using Azure Event Hubs, Fabric eventstreams, and Data Activator.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/monitoring/monitoring-observable-systems-media",
        entry_type="Architecture",
        categories=['Media', 'AI + Machine Learning', 'Analytics'],
        products=['azure-data-explorer', 'azure-functions', 'fabric', 'azure-blob-storage', 'azure-event-hubs'],
    ),
    "migrate_aix_azure_linux": AzureArchitectureEntry(
        key="migrate_aix_azure_linux",
        name="AIX UNIX on-premises to Azure Linux migration",
        summary="Migrate an on-premises IBM AIX system and web application to a highly available, secure RedHat Enterprise Linux system in Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/unix-migration/migrate-aix-azure-linux",
        entry_type="Architecture",
        categories=['Migration', 'Networking'],
        products=['azure-netapp-files', 'azure-site-recovery', 'azure-sql-database', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "apache_kafka_migration": AzureArchitectureEntry(
        key="apache_kafka_migration",
        name="Apache Kafka migration to Azure",
        summary="Learn about Apache Kafka and about ways to migrate a Kafka implementation to Azure by using Azure services like HDInsight and Event Hubs.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/hadoop/apache-kafka-migration",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-hdinsight', 'azure-cosmos-db', 'azure-data-lake-storage', 'azure-stream-analytics'],
    ),
    "microsoft_sentinel_automated_response": AzureArchitectureEntry(
        key="microsoft_sentinel_automated_response",
        name="Microsoft Sentinel automated responses",
        summary="Use Microsoft Sentinel playbook to generate automated responses and deliver intelligent security analytics for enterprises.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/microsoft-sentinel-automated-response",
        entry_type="Solution Idea",
        categories=['Migration', 'Identity', 'Security'],
        products=['microsoft-sentinel', 'entra-id', 'azure-logic-apps'],
    ),
    "ibm_zos_online_transaction_processing_azure": AzureArchitectureEntry(
        key="ibm_zos_online_transaction_processing_azure",
        name="Migrate IBM z/OS OLTP workloads to Azure",
        summary="Migrate a z/OS online transaction processing (OLTP) workload to an Azure application that is cost effective, responsive, scalable, and adaptable.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/ibm-zos-online-transaction-processing-azure",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-front-door', 'azure-traffic-manager', 'azure-kubernetes-service', 'azure-managed-redis'],
    ),
    "migrate_cloud_workloads_across_security_tenants": AzureArchitectureEntry(
        key="migrate_cloud_workloads_across_security_tenants",
        name="Migrate cloud workloads across security tenants",
        summary="Learn how to define and implement a cross-tenant workload migration strategy to address business transformations like acquisitions or divestitures.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/migrate-cloud-workloads-across-security-tenants",
        entry_type="Solution Idea",
        categories=['Migration', 'Management + Governance', 'Security'],
        products=['entra-id', 'azure-devops', 'azure-resource-manager', 'azure-backup'],
    ),
    "guidance": AzureArchitectureEntry(
        key="guidance",
        name="Modern Web App pattern for .NET",
        summary="Modern Web App pattern for .NET. Modernize web apps in the cloud with prescriptive architecture, code, and configuration guidance.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/guides/enterprise-app-patterns/modern-web-app/dotnet/guidance",
        entry_type="Architecture",
        categories=['Migration', 'Web'],
        products=['azure-app-service', 'azure-front-door', 'azure-managed-redis', 'dotnet'],
    ),
    "modernize_mainframe_data_to_azure": AzureArchitectureEntry(
        key="modernize_mainframe_data_to_azure",
        name="Modernize mainframe and midrange data",
        summary="Learn how to modernize IBM mainframe and midrange data. Use a data-first approach to migrate the data to scalable and more secure cloud storage on Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/modernize-mainframe-data-to-azure",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-cosmos-db', 'azure-data-lake', 'azure-sql-database', 'azure-sql-managed-instance', 'azure-storage'],
    ),
    "move_archive_data_mainframes": AzureArchitectureEntry(
        key="move_archive_data_mainframes",
        name="Move archive data from mainframe systems to Azure",
        summary="Learn about a reference architecture that shows how to move data from mainframe and midrange systems to Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/move-archive-data-mainframes",
        entry_type="Architecture",
        categories=['Migration', 'Databases'],
        products=['azure-data-factory', 'azure-storage', 'azure-files', 'azure-blob-storage', 'azure-data-box-family'],
    ),
    "cloudframe_renovate_mainframe_refactor": AzureArchitectureEntry(
        key="cloudframe_renovate_mainframe_refactor",
        name="Refactor mainframe architecture by using CloudFrame Renovate",
        summary="Refactor your mainframe architecture to Azure by using the CloudFrame Renovate code migration tool. Renovate migrates COBOL to Java.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/cloudframe-renovate-mainframe-refactor",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-virtual-machines', 'azure-kubernetes-service', 'azure-virtual-network', 'azure-sql-database', 'azure-site-recovery'],
    ),
    "refactor_adabas_aks": AzureArchitectureEntry(
        key="refactor_adabas_aks",
        name="Refactor mainframe computer systems that run Adabas & Natural",
        summary="Learn how to modernize mainframe computer systems that run Adabas & Natural and move them to the cloud.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/refactor-adabas-aks",
        entry_type="Architecture",
        categories=['Migration', 'Databases', 'Containers'],
        products=['azure-kubernetes-service', 'azure-expressroute', 'azure-managed-disks', 'azure-netapp-files'],
    ),
    "rehost_adabas_software_ag": AzureArchitectureEntry(
        key="rehost_adabas_software_ag",
        name="Rehost Adabas & Natural applications in Azure",
        summary="Learn how to migrate a Software AG Adabas & Natural mainframe system to Azure by using a rehost approach.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/rehost-adabas-software-ag",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-virtual-network', 'azure-virtual-machines', 'azure-expressroute'],
    ),
    "rehost_ims_raincode_imsql": AzureArchitectureEntry(
        key="rehost_ims_raincode_imsql",
        name="Rehost IMS DC and IMS DB on Azure by using Raincode IMSql",
        summary="Learn how to rehost IBM IMS DC and IMS DB on Azure by using Raincode IMSql. Rehost seamlessly without translating or changing your application.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/rehost-ims-raincode-imsql",
        entry_type="Architecture",
        categories=['Migration', 'Databases'],
        products=['azure-vm-scalesets', 'azure-logic-apps', 'azure-sql-managed-instance', 'azure-virtual-network', 'azure-expressroute'],
    ),
    "imsql_rehost_ims": AzureArchitectureEntry(
        key="imsql_rehost_ims",
        name="Rehost IMS workloads to virtual machines by using IMSql",
        summary="Learn how to use IMSql to rehost IMS DB and IMS TM systems on .NET and SQL Server by using virtual machines.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/imsql-rehost-ims",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-virtual-machines', 'azure-virtual-network', 'azure-vm-scalesets', 'azure-sql-managed-instance'],
    ),
    "sync_mainframe_data_with_azure": AzureArchitectureEntry(
        key="sync_mainframe_data_with_azure",
        name="Replicate and sync mainframe data to Azure",
        summary="Learn how to replicate data while you modernize mainframe and midrange systems. Sync on-premises data with Azure data during modernization.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/migration/sync-mainframe-data-with-azure",
        entry_type="Reference Architecture",
        categories=['Migration', 'Databases'],
        products=['azure-data-factory', 'azure-databricks', 'fabric'],
    ),
    "mainframe_data_replication_azure_rdrs": AzureArchitectureEntry(
        key="mainframe_data_replication_azure_rdrs",
        name="Replicate mainframe and midrange data to Azure by using RDRS",
        summary="Learn how to use RDRS, a mainframe data replication solution, to migrate data to and from multiple Azure data platform services.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/mainframe-data-replication-azure-rdrs",
        entry_type="Architecture",
        categories=['Migration', 'Integration', 'Databases'],
        products=['azure-database-migration', 'azure-functions', 'azure-logic-apps', 'azure-sql-database', 'azure-storage'],
    ),
    "mainframe_replication_precisely_connect": AzureArchitectureEntry(
        key="mainframe_replication_precisely_connect",
        name="Replicate mainframe data by using Precisely Connect",
        summary="Learn how to use Precisely Connect to migrate mainframe and midrange systems to the Azure platform.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/mainframe-replication-precisely-connect",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-sql-database', 'azure-sql-managed-instance', 'azure-synapse-analytics', 'azure-databricks', 'azure-event-hubs'],
    ),
    "hp_ux_stromasys_charon_par": AzureArchitectureEntry(
        key="hp_ux_stromasys_charon_par",
        name="Run HP-UX workloads in Azure with Stromasys Charon-PAR",
        summary="Learn how to use a lift-and-shift approach to migrate an HP-UX workload to Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/hp-ux-stromasys-charon-par",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-virtual-machines', 'azure-virtual-network', 'azure-expressroute', 'azure-storage', 'azure-files'],
    ),
    "solaris_azure": AzureArchitectureEntry(
        key="solaris_azure",
        name="Stromasys Charon-SSP Solaris emulator on Azure VMs",
        summary="Charon-SSP cross-platform hypervisor emulates legacy Sun SPARC systems on industry standard x86-64 computer systems and VMs.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/solaris-azure",
        entry_type="Solution Idea",
        categories=['Migration'],
        products=['azure-storage', 'azure-virtual-machines'],
    ),
    "mainframe_midrange_data_replication_azure_qlik": AzureArchitectureEntry(
        key="mainframe_midrange_data_replication_azure_qlik",
        name="Use Qlik to replicate mainframe and midrange data to Azure",
        summary="Learn how to use Qlik Replicate to migrate mainframe and midrange systems to the cloud or extend those systems by using cloud applications.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/mainframe-midrange-data-replication-azure-qlik",
        entry_type="Architecture",
        categories=['Migration'],
        products=['azure-event-hubs', 'azure-data-lake', 'azure-databricks'],
    ),
    "enterprise_file_shares_disaster_recovery": AzureArchitectureEntry(
        key="enterprise_file_shares_disaster_recovery",
        name="Enterprise file shares with disaster recovery",
        summary="Learn how to implement resilient NetApp file shares. Failure of the primary Azure region causes automatic failover to the secondary Azure region.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/file-storage/enterprise-file-shares-disaster-recovery",
        entry_type="Architecture",
        categories=['Networking', 'Storage'],
        products=['azure-netapp-files', 'entra', 'windows-server'],
    ),
    "private_link_virtual_wan_dns_guide": AzureArchitectureEntry(
        key="private_link_virtual_wan_dns_guide",
        name="Guide to Private Link and DNS in Azure Virtual WAN",
        summary="Learn how to implement DNS to support private endpoints in a Virtual WAN network. In these scenarios, every Virtual WAN hub has a firewall that has DNS proxy enabled.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/guide/private-link-virtual-wan-dns-guide",
        entry_type="Architecture",
        categories=['Networking', 'Security'],
        products=['azure-private-link', 'azure-dns', 'azure-firewall', 'azure-virtual-wan'],
    ),
    "hub_spoke": AzureArchitectureEntry(
        key="hub_spoke",
        name="Hub-spoke network topology in Azure",
        summary="Learn about hub-spoke topology in Azure, where the spoke virtual networks connect to the hub virtual network and can connect to each other.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/hub-spoke",
        entry_type="Reference Architecture",
        categories=['Networking', 'Management + Governance', 'Hybrid + Multicloud'],
        products=['azure-bastion', 'azure-firewall', 'azure-network-watcher', 'azure-virtual-network', 'azure-vpn-gateway'],
    ),
    "hub_spoke_virtual_wan_architecture": AzureArchitectureEntry(
        key="hub_spoke_virtual_wan_architecture",
        name="Hub-spoke network topology that uses Azure Virtual WAN",
        summary="Learn how to implement a hub-spoke network topology by using Azure Virtual WAN. Create a hub virtual network and spoke virtual networks that peer with the hub.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/hub-spoke-virtual-wan-architecture",
        entry_type="Architecture",
        categories=['Networking'],
        products=['azure-virtual-wan'],
    ),
    "ipv6_architecture": AzureArchitectureEntry(
        key="ipv6_architecture",
        name="IPv6 hub-spoke network topology",
        summary="Learn how to transition a hub-and-spoke network topology in Azure so it supports IPv6, which creates a dual-stack network.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/guide/ipv6-architecture",
        entry_type="Architecture",
        categories=['Networking', 'Security', 'Management + Governance'],
        products=['azure-firewall', 'azure-virtual-network', 'azure-virtual-wan', 'azure-vpn-gateway'],
    ),
    "trusted_internet_connections": AzureArchitectureEntry(
        key="trusted_internet_connections",
        name="Implement TIC 3.0 compliance",
        summary="Implement Trusted Internet Connection (TIC) 3.0 compliance for your internet-facing Azure applications and services, and improve the user experience.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/trusted-internet-connections",
        entry_type="Architecture",
        categories=['Networking', 'Security', 'Web'],
        products=['azure-firewall', 'azure-application-gateway', 'azure-front-door', 'azure-log-analytics', 'azure-event-hubs'],
    ),
    "secure_vnet_dmz": AzureArchitectureEntry(
        key="secure_vnet_dmz",
        name="Implement a secure hybrid network",
        summary="Learn how to deploy a secure hybrid network that extends an on-premises network to Azure with a perimeter network between the on-premises network and an Azure virtual network.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/dmz/secure-vnet-dmz",
        entry_type="Reference Architecture",
        categories=['Networking', 'Security', 'Hybrid + Multicloud'],
        products=['azure-firewall', 'azure-load-balancer', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "massive_scale_azure_architecture": AzureArchitectureEntry(
        key="massive_scale_azure_architecture",
        name="Massive-scale VWAN architecture design",
        summary="Learn about the architecture for a massive-scale Azure Virtual WAN deployment that has multiple hubs per region.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/massive-scale-azure-architecture",
        entry_type="Architecture",
        categories=['Networking', 'Security'],
        products=['azure-virtual-wan', 'azure-vm-scalesets', 'azure-expressroute'],
    ),
    "traffic_manager_application_gateway": AzureArchitectureEntry(
        key="traffic_manager_application_gateway",
        name="Multiregion load balancing",
        summary="Learn how to build an Azure system that serves web and non-web workloads with resilient multitier applications in multiple Azure regions.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/high-availability/traffic-manager-application-gateway",
        entry_type="Reference Architecture",
        categories=['Networking', 'Web'],
        products=['azure-firewall', 'azure-application-gateway', 'azure-load-balancer', 'azure-traffic-manager'],
    ),
    "sdwan_integration_in_hub_and_spoke_network_topologies": AzureArchitectureEntry(
        key="sdwan_integration_in_hub_and_spoke_network_topologies",
        name="SDWAN integration with Azure hub-and-spoke network topologies",
        summary="Learn about architecture patterns for SDWAN integration with Azure hub-and-spoke network topologies, based on the Azure Well-Architected Framework\'s five pillars of architecture excellence.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/guide/sdwan-integration-in-hub-and-spoke-network-topologies",
        entry_type="Architecture",
        categories=['Networking'],
        products=['azure-expressroute', 'azure-vpn-gateway', 'azure-virtual-network'],
    ),
    "private_link_virtual_wan_dns_single_region_workload": AzureArchitectureEntry(
        key="private_link_virtual_wan_dns_single_region_workload",
        name="Single region scenario - Private Link and DNS in Azure Virtual WAN",
        summary="This article provides guidance on implementing DNS to support private endpoints in a Virtual WAN network in a single region where the virtual hub has a Firewall with DNS Proxy enabled. The solution...",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/guide/private-link-virtual-wan-dns-single-region-workload",
        entry_type="Architecture",
        categories=['Networking', 'Security'],
        products=['azure-private-link', 'azure-dns', 'azure-firewall', 'azure-virtual-wan'],
    ),
    "split_brain_dns": AzureArchitectureEntry(
        key="split_brain_dns",
        name="Use a split-brain DNS configuration to host a web app in Azure",
        summary="Implement a split-brain DNS configuration to differentiate traffic treatment based on DNS and whether a client originates from the internet or a corporate network.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/networking/split-brain-dns",
        entry_type="Architecture",
        categories=['Networking', 'Security', 'Web', 'Hybrid + Multicloud'],
        products=['azure-front-door', 'azure-application-gateway', 'azure-expressroute', 'azure-dns'],
    ),
    "performance_security_optimized_vwan": AzureArchitectureEntry(
        key="performance_security_optimized_vwan",
        name="Virtual WAN architecture optimized for department-specific requirements",
        summary="Learn how to design a single network that has varying security and performance requirements.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/performance-security-optimized-vwan",
        entry_type="Architecture",
        categories=['Networking', 'Security'],
        products=['azure-virtual-wan', 'azure-expressroute', 'azure-virtual-network'],
    ),
    "private_link_virtual_wan_dns_virtual_hub_extension_pattern": AzureArchitectureEntry(
        key="private_link_virtual_wan_dns_virtual_hub_extension_pattern",
        name="Virtual hub extension pattern",
        summary="This article describes a pattern for exposing shared services, such as DNS, in a hub-and-spoke topology that uses Azure Virtual WAN.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/guide/private-link-virtual-wan-dns-virtual-hub-extension-pattern",
        entry_type="Architecture",
        categories=['Networking', 'Security'],
        products=['azure-private-link', 'azure-dns', 'azure-firewall', 'azure-virtual-wan'],
    ),
    "virtual_network_peering": AzureArchitectureEntry(
        key="virtual_network_peering",
        name="Virtual network connectivity options and spoke-to-spoke communication",
        summary="Compare virtual network peering and VPN gateways for Azure connectivity. Learn spoke-to-spoke communication patterns in hub-and-spoke architectures.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/virtual-network-peering",
        entry_type="Reference Architecture",
        categories=['Networking', 'Integration'],
        products=['entra-id', 'azure-virtual-network', 'azure-vpn-gateway', 'virtual-network-manager'],
    ),
    "index": AzureArchitectureEntry(
        key="index",
        name="Certificate lifecycle management on Azure",
        summary="Learn how to create an infrastructure and workflow to automate the renewal process for certificates issued by a nonintegrated certification authority (CA).",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/certificate-lifecycle/index",
        entry_type="Architecture",
        categories=['Security'],
        products=['azure-automation', 'azure-event-grid', 'azure-key-vault'],
    ),
    "secure_hybrid_messaging_client": AzureArchitectureEntry(
        key="secure_hybrid_messaging_client",
        name="Enhanced-security hybrid messaging infrastructure for desktop-client access",
        summary="Enhance your security in a desktop-client access scenario by using Microsoft Entra multifactor authentication.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/hybrid/secure-hybrid-messaging-client",
        entry_type="Architecture",
        categories=['Security', 'Hybrid + Multicloud', 'Identity'],
        products=['entra-id', 'm365', 'office-365'],
    ),
    "secure_hybrid_messaging_mobile": AzureArchitectureEntry(
        key="secure_hybrid_messaging_mobile",
        name="Enhanced-security hybrid messaging infrastructure for mobile access",
        summary="Enhance your security in a mobile access scenario by using Microsoft Entra multifactor authentication.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/hybrid/secure-hybrid-messaging-mobile",
        entry_type="Architecture",
        categories=['Security', 'Hybrid + Multicloud', 'Identity', 'Mobile'],
        products=['entra-id', 'm365', 'office-365'],
    ),
    "secure_hybrid_messaging_web": AzureArchitectureEntry(
        key="secure_hybrid_messaging_web",
        name="Enhanced-security hybrid messaging infrastructure for web access",
        summary="Enhance your security in a web access scenario by using Microsoft Entra multifactor authentication.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/hybrid/secure-hybrid-messaging-web",
        entry_type="Architecture",
        categories=['Security', 'Hybrid + Multicloud', 'Identity', 'Web'],
        products=['entra-id', 'm365', 'office-365'],
    ),
    "access_multitenant_web_app_from_on_premises": AzureArchitectureEntry(
        key="access_multitenant_web_app_from_on_premises",
        name="Improved-security access to App Service web apps from an on-premises network",
        summary="This reference architecture shows how to set up improved-security private connectivity to an App Service web app or function app from an on-premises network or from within an Azure virtual network.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/guides/networking/access-multitenant-web-app-from-on-premises",
        entry_type="Architecture",
        categories=['Security', 'Web'],
        products=['azure-app-service', 'azure-virtual-network', 'azure-private-link', 'azure-key-vault', 'azure-storage-accounts'],
    ),
    "monitoring": AzureArchitectureEntry(
        key="monitoring",
        name="Monitoring and diagnostics guidance",
        summary="Learn how to track how users use your distributed applications and services, trace resource utilization, and monitor the health and performance.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/best-practices/monitoring",
        entry_type="Best Practice",
        categories=['Security'],
        products=['azure-monitor'],
    ),
    "multilayered_protection_azure_vm": AzureArchitectureEntry(
        key="multilayered_protection_azure_vm",
        name="Multilayered protection for Azure virtual machine access",
        summary="Apply the defense in depth strategy by challenging users with multiple lines of defense before they can access your Azure VMs. Ensure that users are legitimate, have legal intentions, and communica...",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/multilayered-protection-azure-vm",
        entry_type="Solution Idea",
        categories=['Security', 'Identity', 'Management + Governance'],
        products=['entra-id', 'azure-bastion', 'azure-rbac', 'defender-for-cloud', 'azure-key-vault'],
    ),
    "fully_managed_secure_apps": AzureArchitectureEntry(
        key="fully_managed_secure_apps",
        name="Securely managed web applications",
        summary="Learn how to deploy secure applications by using the App Service Environment, Azure Application Gateway, and Web Application Firewall.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/apps/fully-managed-secure-apps",
        entry_type="Architecture",
        categories=['Security', 'Web'],
        products=['azure-app-service', 'azure-application-gateway', 'azure-sql-database', 'azure-vpn-gateway', 'azure-web-application-firewall'],
    ),
    "security_start_here": AzureArchitectureEntry(
        key="security_start_here",
        name="Security architecture design",
        summary="Get an overview of Azure security technologies, guidance offerings, solution ideas, and reference architectures.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/security/security-start-here",
        entry_type="Architecture",
        categories=['Security', 'Identity', 'Management + Governance'],
        products=['entra-id', 'azure-firewall', 'azure-front-door', 'azure-key-vault', 'azure-private-link'],
    ),
    "cdn": AzureArchitectureEntry(
        key="cdn",
        name="CDN guidance",
        summary="Guidance on using Content Delivery Networks (CDNs) to deliver high-bandwidth content hosted in Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/best-practices/cdn",
        entry_type="Best Practice",
        categories=['Storage'],
        products=['azure-storage', 'azure-blob-storage'],
    ),
    "data_partitioning": AzureArchitectureEntry(
        key="data_partitioning",
        name="Data partitioning guidance",
        summary="View guidance for how to separate data partitions to be managed and accessed separately. Understand horizontal, vertical, and functional partitioning strategies.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/best-practices/data-partitioning",
        entry_type="Best Practice",
        categories=['Storage'],
        products=['azure-blob-storage'],
    ),
    "data_partitioning_strategies": AzureArchitectureEntry(
        key="data_partitioning_strategies",
        name="Data partitioning strategies",
        summary="View guidance on separating data partitions to be managed and accessed separately in different services, such as Azure AI Search, Azure storage queues, and more.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/best-practices/data-partitioning-strategies",
        entry_type="Best Practice",
        categories=['Storage'],
        products=['azure-table-storage'],
    ),
    "teamcenter_baseline": AzureArchitectureEntry(
        key="teamcenter_baseline",
        name="Siemens Teamcenter baseline architecture on Azure",
        summary="Learn about the Siemens Teamcenter product lifecycle management (PLM) solution architecture on Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/manufacturing/teamcenter-baseline",
        entry_type="Architecture",
        categories=['Storage'],
        products=['azure-virtual-machines', 'azure-sql-database'],
    ),
    "teamcenter_plm_netapp_files": AzureArchitectureEntry(
        key="teamcenter_plm_netapp_files",
        name="Use Teamcenter PLM with Azure NetApp Files",
        summary="Learn how to use Azure NetApp Files as a storage solution for Siemens Teamcenter product lifecycle management (PLM).",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/manufacturing/teamcenter-plm-netapp-files",
        entry_type="Architecture",
        categories=['Storage'],
        products=['azure-netapp-files', 'azure-sql-database'],
    ),
    "baseline_zone_redundant": AzureArchitectureEntry(
        key="baseline_zone_redundant",
        name="Baseline highly available zone-redundant web application",
        summary="Learn about a baseline reference architecture for a network secured, highly available, and zone-redundant Azure App Service web application.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service/architectures/baseline-zone-redundant",
        entry_type="Reference Architecture",
        categories=['Web', 'Management + Governance'],
        products=['azure-app-service', 'azure-application-gateway', 'azure-storage', 'azure-sql-database', 'azure-private-link'],
    ),
    "basic_web_app": AzureArchitectureEntry(
        key="basic_web_app",
        name="Basic web application",
        summary="Learn about proven practices for deploying web applications that use Azure App Service and Azure SQL Database.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service/architectures/basic-web-app",
        entry_type="Reference Architecture",
        categories=['Web'],
        products=['azure-app-service', 'azure-monitor', 'azure-sql-database'],
    ),
    "orchestration": AzureArchitectureEntry(
        key="orchestration",
        name="Container orchestration for microservices",
        summary="Learn how container orchestration makes it easy to manage complex multi-container microservice deployments, scaling, and cluster health.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/microservices/design/orchestration",
        entry_type="Architecture",
        categories=['Web', 'Developer Tools'],
        products=['azure-kubernetes-service', 'azure-container-apps', 'azure-container-instances'],
    ),
    "highly_available_sharepoint_farm": AzureArchitectureEntry(
        key="highly_available_sharepoint_farm",
        name="Highly available SharePoint farm",
        summary="Deploy a highly available SharePoint farm for intranet capabilities that uses Microsoft Entra ID, a SQL always on instance, and SharePoint resources.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/highly-available-sharepoint-farm",
        entry_type="Solution Idea",
        categories=['Web', 'Management + Governance'],
        products=['entra-id', 'azure-load-balancer', 'sql-server'],
    ),
    "apim_api_scenario": AzureArchitectureEntry(
        key="apim_api_scenario",
        name="Migrate a web app by using Azure API Management",
        summary="Review an example scenario in which an e-commerce company in the travel industry uses Azure API Management to migrate a legacy web application.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/apps/apim-api-scenario",
        entry_type="Architecture",
        categories=['Web', 'Migration', 'Integration'],
        products=['azure-api-management', 'azure-monitor', 'azure-app-service'],
    ),
    "multi_region_app_service": AzureArchitectureEntry(
        key="multi_region_app_service",
        name="Multi-region App Service app approaches for disaster recovery",
        summary="Learn about common approaches to deploy Azure App Service apps across multiple regions for disaster recovery purposes.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/guides/multi-region-app-service/multi-region-app-service",
        entry_type="Architecture",
        categories=['Web'],
        products=['azure-app-service', 'azure-front-door'],
    ),
    "multi_tier_app_disaster_recovery": AzureArchitectureEntry(
        key="multi_tier_app_disaster_recovery",
        name="Multitier web application built for high availability and disaster recovery",
        summary="Create a multitier web application built for high availability and disaster recovery on Azure by using Azure virtual machines, availability sets, availability zones, Azure Site Recovery, and Azure ...",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/infrastructure/multi-tier-app-disaster-recovery",
        entry_type="Architecture",
        categories=['Web', 'Featured'],
        products=['azure', 'azure-arc', 'sql-server', 'windows'],
    ),
    "protect_apis": AzureArchitectureEntry(
        key="protect_apis",
        name="Protect APIs by using Application Gateway and API Management",
        summary="Learn how to protect APIs with API Management and Application Gateway.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/api-management/architectures/protect-apis",
        entry_type="Reference Architecture",
        categories=['Web', 'Security'],
        products=['azure-api-management', 'azure-application-gateway'],
    ),
    "sap_s4_hana_on_hli_with_ha_and_dr": AzureArchitectureEntry(
        key="sap_s4_hana_on_hli_with_ha_and_dr",
        name="SAP S/4 HANA for Large Instances",
        summary="With large SAP HANA instances, use Azure Virtual Machines, OS clustering, and NFS storage for scalability, performance, high reliability, and disaster recovery.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/sap-s4-hana-on-hli-with-ha-and-dr",
        entry_type="Solution Idea",
        categories=['Web', 'Storage', 'Compute'],
        products=['azure-expressroute', 'azure-files', 'azure-sap', 'azure-virtual-machines'],
    ),
    "scalable_apps_performance_modeling_site_reliability": AzureArchitectureEntry(
        key="scalable_apps_performance_modeling_site_reliability",
        name="Scalable cloud applications and site reliability engineering (SRE)",
        summary="Build scalable cloud applications by using performance modeling and other principles and practices of site reliability engineering (SRE).",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/apps/scalable-apps-performance-modeling-site-reliability",
        entry_type="Architecture",
        categories=['Web', 'Developer Tools'],
        products=['azure-front-door', 'azure-api-management', 'azure-kubernetes-service', 'azure-application-gateway'],
    ),
    "gateway": AzureArchitectureEntry(
        key="gateway",
        name="Use API gateways in microservices",
        summary="An API gateway sits between clients and services and acts as a reverse proxy. Learn how to choose an API gateway technology for a microservice.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/microservices/design/gateway",
        entry_type="Architecture",
        categories=['Web', 'Developer Tools'],
        products=['azure-application-gateway', 'azure-api-management'],
    ),
    "wordpress_app_service": AzureArchitectureEntry(
        key="wordpress_app_service",
        name="WordPress on App Service",
        summary="Use Azure Front Door, Azure App Service, and other Azure services to deploy a highly scalable and secure installation of WordPress.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/infrastructure/wordpress-app-service",
        entry_type="Architecture",
        categories=['Web'],
        products=['azure-front-door', 'azure-load-balancer', 'azure-virtual-network', 'azure-app-service', 'azure-database-mysql'],
    ),
    "wordpress_container": AzureArchitectureEntry(
        key="wordpress_container",
        name="WordPress on Azure Kubernetes Service",
        summary="\"Use Azure Kubernetes Service (AKS) to deploy a highly scalable and secure installation of WordPress for large, storage-intensive applications.\"",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/infrastructure/wordpress-container",
        entry_type="Architecture",
        categories=['Web', 'Containers'],
        products=['azure-managed-redis', 'azure-front-door', 'azure-kubernetes-service', 'azure-load-balancer', 'azure-netapp-files'],
    ),
    "arc_hybrid_kubernetes": AzureArchitectureEntry(
        key="arc_hybrid_kubernetes",
        name="Azure Arc hybrid management and deployment for Kubernetes clusters",
        summary="Learn how Azure Arc extends Kubernetes cluster management and configuration across customer data centers, edge locations, and multiple cloud environments.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/arc-hybrid-kubernetes",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Management + Governance'],
        products=['azure-arc', 'azure-kubernetes-service', 'azure-monitor', 'azure-policy', 'azure-rbac'],
    ),
    "azure_dns_private_resolver": AzureArchitectureEntry(
        key="azure_dns_private_resolver",
        name="Azure DNS Private Resolver",
        summary="Learn how to use Azure DNS Private Resolver to simplify hybrid recursive Domain Name System (DNS) resolution for on-premises and Azure workloads.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/azure-dns-private-resolver",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Networking'],
        products=['azure-dns', 'azure-expressroute', 'azure-firewall', 'azure-virtual-network', 'azure-vpn-gateway'],
    ),
    "azure_files_on_premises_authentication": AzureArchitectureEntry(
        key="azure_files_on_premises_authentication",
        name="Azure Files accessed from on-premises and secured by AD DS in a private network",
        summary="Learn how to provide on-premises access to Azure Files with security provided by on-premises Windows Server Active Directory Domain Services (AD DS).",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/hybrid/azure-files-on-premises-authentication",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Storage', 'Security'],
        products=['azure-virtual-network', 'azure-expressroute', 'azure-storage-accounts', 'azure-files', 'azure-dns'],
    ),
    "aks_baseline": AzureArchitectureEntry(
        key="aks_baseline",
        name="Azure Kubernetes Service (AKS) Baseline Architecture for AKS on Azure Local",
        summary="Learn how to design and implement a baseline architecture for Microsoft Azure Kubernetes Service (AKS) that runs on Azure Local.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/hybrid/aks-baseline",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Compute'],
        products=['azure-kubernetes-service', 'azure-local', 'azure-arc'],
    ),
    "azure_local_baseline": AzureArchitectureEntry(
        key="azure_local_baseline",
        name="Azure Local baseline reference architecture",
        summary="Learn how to design Azure Local for highly available virtualized and containerized workloads.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/azure-local-baseline",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Management + Governance'],
        products=['azure-local', 'azure-arc', 'azure-key-vault', 'azure-monitor', 'defender-for-cloud'],
    ),
    "azure_local_switchless": AzureArchitectureEntry(
        key="azure_local_switchless",
        name="Azure Local storage switchless architecture",
        summary="Learn how to design Azure Local infrastructure by using a storage switchless architecture.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/azure-local-switchless",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Management + Governance'],
        products=['azure-local', 'azure-arc', 'azure-key-vault', 'azure-monitor', 'defender-for-cloud'],
    ),
    "azure_local_workload_virtual_desktop": AzureArchitectureEntry(
        key="azure_local_workload_virtual_desktop",
        name="Azure Virtual Desktop for Azure Local",
        summary="Learn how to design Azure Virtual Desktop for Azure Local to provide a more secure and productive remote desktop experience for users.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/azure-local-workload-virtual-desktop",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Management + Governance'],
        products=['azure-local', 'entra-id', 'azure-virtual-desktop'],
    ),
    "azure_files_private": AzureArchitectureEntry(
        key="azure_files_private",
        name="Azure enterprise cloud file share",
        summary="Learn about an enterprise-level cloud file sharing solution that uses Azure Files, Azure File Sync, Azure Private DNS, and Azure Private Endpoint.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/azure-files-private",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Storage'],
        products=['azure-dns', 'azure-files', 'azure-private-link', 'azure-storage', 'azure-virtual-network'],
    ),
    "expressroute_vpn_failover": AzureArchitectureEntry(
        key="expressroute_vpn_failover",
        name="Connect an on-premises network to Azure using ExpressRoute",
        summary="Implement a highly available and secure site-to-site network architecture that spans an Azure virtual network and an on-premises network connected using ExpressRoute with VPN gateway failover.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/expressroute-vpn-failover",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Networking'],
        products=['azure-expressroute', 'azure-virtual-network', 'azure-vpn-gateway'],
    ),
    "arc_sql_managed_instance_disaster_recovery": AzureArchitectureEntry(
        key="arc_sql_managed_instance_disaster_recovery",
        name="Deploy an Azure Arc-enabled SQL managed instance for disaster recovery",
        summary="Use Azure Arc to deploy an Azure Arc-enabled SQL managed instance across two sites that are outside of Azure in a highly available architecture.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/arc-sql-managed-instance-disaster-recovery",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Databases'],
        products=['azure-arc', 'azure-sql-managed-instance'],
    ),
    "hybrid_dns_infra": AzureArchitectureEntry(
        key="hybrid_dns_infra",
        name="Design a hybrid Domain Name System (DNS) solution by using Azure",
        summary="Learn how to design a hybrid Domain Name System (DNS) solution to resolve names for workloads that are hosted on-premises and in Microsoft Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/hybrid-dns-infra",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Networking'],
        products=['azure-bastion', 'azure-dns', 'azure-expressroute', 'azure-virtual-network'],
    ),
    "adfs": AzureArchitectureEntry(
        key="adfs",
        name="Extend on-premises Active Directory Federation Services to Azure",
        summary="Implement a secure hybrid network architecture with Active Directory Federation Services authorization and identity federation in Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/identity/adfs",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Identity'],
        products=['azure-load-balancer', 'entra', 'entra-id'],
    ),
    "general_mainframe_refactor": AzureArchitectureEntry(
        key="general_mainframe_refactor",
        name="General mainframe refactor to Azure",
        summary="Learn how to refactor general mainframe applications to run more cost-effectively and efficiently on Azure by using AKS or virtual machines.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/general-mainframe-refactor",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Migration'],
        products=['azure-files', 'azure-load-balancer', 'azure-sql-database', 'azure-storage', 'azure-virtual-machines'],
    ),
    "hybrid_perf_monitoring": AzureArchitectureEntry(
        key="hybrid_perf_monitoring",
        name="Hybrid availability and performance monitoring",
        summary="Use Azure Monitor to monitor performance and availability for OS workloads running on-premises, in third-party cloud providers, and in Microsoft Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/hybrid-perf-monitoring",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Management + Governance'],
        products=['azure-event-hubs', 'azure-log-analytics', 'azure-monitor', 'azure-storage', 'azure-virtual-machines'],
    ),
    "hybrid_file_services": AzureArchitectureEntry(
        key="hybrid_file_services",
        name="Hybrid file services",
        summary="Use Azure File Sync and Azure Files to extend file services hosting capabilities across cloud and on-premises file share resources.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/hybrid-file-services",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Storage'],
        products=['entra-id', 'azure-expressroute', 'azure-files', 'azure-storage-accounts'],
    ),
    "avanade_amt_zos_migration": AzureArchitectureEntry(
        key="avanade_amt_zos_migration",
        name="IBM z/OS mainframe migration with Avanade AMT",
        summary="See how to use the Avanade Automated Migration Technology (AMT) framework to migrate IBM z/OS mainframe workloads to Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/avanade-amt-zos-migration",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Migration'],
        products=['azure-load-balancer', 'azure-sql-database', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
    "integrate_ibm_message_queues_azure": AzureArchitectureEntry(
        key="integrate_ibm_message_queues_azure",
        name="Integrate IBM mainframe and midrange message queues with Azure",
        summary="This example describes a data-first approach to middleware integration that enables IBM message queues (MQs).",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/integrate-ibm-message-queues-azure",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Integration'],
        products=['azure-logic-apps', 'azure-sql-database', 'azure-sql-managed-instance', 'azure-sql-virtual-machines', 'azure-database-postgresql'],
    ),
    "azure_ad": AzureArchitectureEntry(
        key="azure_ad",
        name="Integrate on-premises Active Directory domains with Microsoft Entra ID",
        summary="Learn how to implement a secure hybrid network architecture that integrates on-premises Active Directory domains with Microsoft Entra ID.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/identity/azure-ad",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Identity'],
        products=['azure-virtual-machines', 'azure-virtual-network', 'entra-id'],
    ),
    "migrate_aix_workloads_to_azure_with_skytap": AzureArchitectureEntry(
        key="migrate_aix_workloads_to_azure_with_skytap",
        name="Migrate AIX workloads to Azure with Skytap",
        summary="This example illustrates a migration of AIX logical partitions (LPARs) to Skytap on Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/migrate-aix-workloads-to-azure-with-skytap",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Migration'],
        products=['azure-virtual-network', 'azure-private-link', 'azure-expressroute', 'azure-virtual-machines', 'azure-data-box-family'],
    ),
    "migrate_ibm_i_series_to_azure_with_skytap": AzureArchitectureEntry(
        key="migrate_ibm_i_series_to_azure_with_skytap",
        name="Migrate IBM i series to Azure with Skytap",
        summary="This example architecture shows how to use the native IBM i backup and recovery services with Microsoft Azure components.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/migrate-ibm-i-series-to-azure-with-skytap",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Migration'],
        products=['azure-virtual-network', 'azure-private-link', 'azure-expressroute', 'azure-virtual-machines', 'azure-data-box-family'],
    ),
    "azure_arc_sql_server": AzureArchitectureEntry(
        key="azure_arc_sql_server",
        name="Optimize administration of SQL Server instances in on-premises and multicloud environments using Azure Arc",
        summary="Optimize management, maintenance, and monitoring of SQL Server with Azure Arc enabled SQL Server and Azure Arc enabled data services in on-premises and multicloud environments.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/azure-arc-sql-server",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Databases'],
        products=['azure-arc', 'sql-server', 'azure-kubernetes-service', 'azure-resource-manager', 'azure-sql-managed-instance'],
    ),
    "troubleshoot_vpn": AzureArchitectureEntry(
        key="troubleshoot_vpn",
        name="Troubleshoot a hybrid VPN connection",
        summary="Troubleshoot a VPN gateway connection between an on-premises network and Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/troubleshoot-vpn",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Networking'],
        products=['azure-virtual-network', 'azure-vpn-gateway', 'windows-server'],
    ),
    "migrate_unisys_dorado_mainframe_apps_with_astadia_micro_focus": AzureArchitectureEntry(
        key="migrate_unisys_dorado_mainframe_apps_with_astadia_micro_focus",
        name="Unisys Dorado mainframe migration to Azure with Astadia and Micro Focus",
        summary="Migrate Unisys Dorado mainframe systems with Astadia and Micro Focus products. Move to Azure without rewriting code, switching data models, or updating screens.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/migrate-unisys-dorado-mainframe-apps-with-astadia-micro-focus",
        entry_type="Architecture",
        categories=['Hybrid + Multicloud', 'Migration'],
        products=['azure-data-factory', 'azure-sql-database', 'azure-storage', 'azure-virtual-machines'],
    ),
    "azure_file_share": AzureArchitectureEntry(
        key="azure_file_share",
        name="Use Azure file shares in a hybrid environment",
        summary="With identity-based authentication, you can control access to Azure file shares by using the Active Directory Domain Services.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/hybrid/azure-file-share",
        entry_type="Reference Architecture",
        categories=['Hybrid + Multicloud', 'Storage'],
        products=['entra-id', 'azure-files'],
    ),
    "app_service_environment_standard_deployment": AzureArchitectureEntry(
        key="app_service_environment_standard_deployment",
        name="Enterprise deployment that uses App Service Environment",
        summary="Recommended architecture for deploying an enterprise application by using App Service Environment.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service-environment/architectures/app-service-environment-standard-deployment",
        entry_type="Reference Architecture",
        categories=['Management + Governance', 'Featured'],
        products=['entra-id', 'azure-application-gateway', 'azure-app-service', 'azure-firewall', 'azure-virtual-network'],
    ),
    "app_service_environment_high_availability_deployment": AzureArchitectureEntry(
        key="app_service_environment_high_availability_deployment",
        name="High availability enterprise deployment that uses App Service Environment",
        summary="Learn about the recommended architecture to deploy an enterprise application by using App Service Environment in multiple availability zones.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service-environment/architectures/app-service-environment-high-availability-deployment",
        entry_type="Reference Architecture",
        categories=['Management + Governance', 'Featured'],
        products=['entra-id', 'azure-application-gateway', 'azure-firewall', 'azure-virtual-network', 'azure-app-service'],
    ),
    "manage_microsoft_365_tenant_configuration_microsoft365dsc_devops": AzureArchitectureEntry(
        key="manage_microsoft_365_tenant_configuration_microsoft365dsc_devops",
        name="Manage Microsoft 365 tenant configuration by using Microsoft365DSC and Azure DevOps",
        summary="Manage Microsoft 365 tenant configuration by using Microsoft365DSC and Azure DevOps.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/example-scenario/devops/manage-microsoft-365-tenant-configuration-microsoft365dsc-devops",
        entry_type="Architecture",
        categories=['Management + Governance', 'DevOps'],
        products=['azure-devops', 'azure-key-vault', 'azure-virtual-machines-windows', 'm365'],
    ),
    "mainframe_azure_file_replication": AzureArchitectureEntry(
        key="mainframe_azure_file_replication",
        name="Mainframe file replication and sync on Azure",
        summary="Learn about several options for moving, converting, transforming, and storing mainframe and midrange file system data on-premises and in Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/mainframe-azure-file-replication",
        entry_type="Solution Idea",
        categories=[],
        products=['azure-data-factory', 'azure-data-lake', 'azure-sql-database', 'azure-storage', 'azure-virtual-machines'],
    ),
    "unisys_mainframe_migration": AzureArchitectureEntry(
        key="unisys_mainframe_migration",
        name="Unisys mainframe migration with Avanade AMT",
        summary="Learn about options for using the Avanade Automated Migration Technology (AMT) Framework to migrate Unisys mainframe workloads to Azure.",
        source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/migration/unisys-mainframe-migration",
        entry_type="Reference Architecture",
        categories=[],
        products=['azure-bastion', 'azure-expressroute', 'azure-sql-database', 'azure-virtual-machines', 'azure-virtual-network'],
    ),
}


def list_architecture_catalog(category: str = "", entry_type: str = "") -> list[dict[str, Any]]:
    """List architectures from the Azure Architecture Catalog, optionally filtered."""
    results = []
    for entry in AZURE_ARCHITECTURE_CATALOG.values():
        if category and not any(category.lower() in c.lower() for c in entry.categories):
            continue
        if entry_type and entry_type.lower() not in entry.entry_type.lower():
            continue
        results.append({
            "key": entry.key,
            "name": entry.name,
            "summary": entry.summary,
            "source_url": entry.source_url,
            "type": entry.entry_type,
            "categories": entry.categories,
        })
    return results


def search_architecture_catalog(query: str) -> list[dict[str, Any]]:
    """Search the architecture catalog by name, summary, category, or products."""
    q = query.lower()
    scored: list[tuple[int, AzureArchitectureEntry]] = []

    for entry in AZURE_ARCHITECTURE_CATALOG.values():
        score = 0
        name_lower = entry.name.lower()
        summary_lower = entry.summary.lower()

        # Exact name match
        if q in name_lower:
            score += 10
        # Key match
        if q.replace(" ", "_") in entry.key:
            score += 8
        # Word matches in name
        for word in q.split():
            if len(word) > 2 and word in name_lower:
                score += 3
            if len(word) > 3 and word in summary_lower:
                score += 1
        # Category match
        for cat in entry.categories:
            if q in cat.lower():
                score += 5
        # Product match
        for prod in entry.products:
            prod_name = prod.replace("-", " ")
            if q in prod_name:
                score += 3

        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "key": entry.key,
            "name": entry.name,
            "score": score,
            "summary": entry.summary,
            "source_url": entry.source_url,
            "type": entry.entry_type,
            "categories": entry.categories,
            "products": entry.products,
        }
        for score, entry in scored[:15]
    ]


def get_architecture_catalog_entry(key: str) -> dict[str, Any] | None:
    """Get full details for an architecture catalog entry."""
    entry = AZURE_ARCHITECTURE_CATALOG.get(key)
    if not entry:
        return None
    return {
        "key": entry.key,
        "name": entry.name,
        "summary": entry.summary,
        "source_url": entry.source_url,
        "type": entry.entry_type,
        "categories": entry.categories,
        "products": entry.products,
    }


def get_architecture_style(key: str) -> ArchitectureStyle | None:
    """Look up an architecture style by key."""
    return ARCHITECTURE_STYLES.get(key)


def list_architecture_styles() -> list[dict[str, Any]]:
    """List all available architecture styles."""
    return [
        {
            "key": style.key,
            "name": style.name,
            "description": style.description,
            "source_url": style.source_url,
            "when_to_use": style.when_to_use,
            "flow_direction": style.flow_direction,
        }
        for style in ARCHITECTURE_STYLES.values()
    ]


def suggest_style_for_description(description: str) -> list[dict[str, Any]]:
    """Suggest architecture styles based on a workload description.

    Performs keyword matching against style descriptions, use-cases,
    and typical components to rank the best-fit styles.
    """
    desc_lower = description.lower()
    scored: list[tuple[int, ArchitectureStyle]] = []

    for style in ARCHITECTURE_STYLES.values():
        score = 0
        # Check style name/description
        if style.key.replace("_", " ") in desc_lower:
            score += 10
        for word in style.name.lower().split():
            if word in desc_lower:
                score += 3
        # Check when_to_use
        for use_case in style.when_to_use:
            for word in use_case.lower().split():
                if len(word) > 4 and word in desc_lower:
                    score += 1
        # Check typical components
        for comp in style.typical_components:
            for word in comp.lower().split():
                if len(word) > 4 and word in desc_lower:
                    score += 1
        # Check azure services
        for svc in style.azure_services:
            svc_name = svc.replace("_", " ")
            if svc_name in desc_lower:
                score += 2
        if score > 0:
            scored.append((score, style))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "key": style.key,
            "name": style.name,
            "score": score,
            "description": style.description,
            "when_to_use": style.when_to_use,
            "typical_components": style.typical_components,
            "azure_services": style.azure_services,
            "diagram_conventions": style.diagram_conventions,
        }
        for score, style in scored[:3]
    ]


# ── Workflow step numbering ──────────────────────────────────────

@dataclass
class WorkflowStep:
    """A numbered workflow step shown on the diagram."""
    number: int
    description: str
    source_id: str
    target_id: str
    connection_type: str = "data_flow"


# ── Reference architecture template definition ───────────────────

@dataclass
class ResourceTemplate:
    """A resource to place in the reference architecture."""
    resource_type: str
    resource_id: str
    display_name: str
    group_id: str         # Boundary it belongs to
    properties: dict = field(default_factory=dict)


@dataclass
class ConnectionTemplate:
    """A connection in the reference architecture."""
    source_id: str
    target_id: str
    label: str
    connection_type: str = "data_flow"
    workflow_step: int | None = None  # Optional numbered step


@dataclass
class BoundaryTemplate:
    """A boundary/grouping in the reference architecture."""
    boundary_id: str
    boundary_type: str
    display_name: str
    parent_id: str | None = None


@dataclass
class ReferenceArchitecture:
    """Complete reference architecture template from Azure Architecture Center."""
    name: str
    description: str
    source_url: str
    category: str                         # e.g., "AI + Machine Learning", "Web", "Networking"
    boundaries: list[BoundaryTemplate]
    resources: list[ResourceTemplate]
    connections: list[ConnectionTemplate]
    workflow_steps: list[WorkflowStep]
    layout_strategy: str = "tiered"
    flow_direction: str = "TB"            # TB or LR
    waf_notes: dict[str, str] = field(default_factory=dict)
    caf_notes: dict[str, str] = field(default_factory=dict)
    # Explicit layout hints: element_id → (x, y) in inches
    layout_hints: dict[str, tuple[float, float]] = field(default_factory=dict)
    # Boundary layout hints: boundary_id → (x, y, width, height) in inches
    boundary_hints: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)


# ═════════════════════════════════════════════════════════════════
# REFERENCE ARCHITECTURE: Baseline Foundry Chat (E2E AI Chat)
# Source: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
# ═════════════════════════════════════════════════════════════════

BASELINE_FOUNDRY_CHAT = ReferenceArchitecture(
    name="Baseline End-to-End Chat with Microsoft Foundry",
    description=(
        "Enterprise chat application using Foundry Agent Service with "
        "App Service frontend, private networking, and WAF-aligned security. "
        "Follows the Azure Architecture Center baseline pattern."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat",
    category="AI + Machine Learning",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "Production Subscription"),
        BoundaryTemplate("rg-network", "resource_group", "rg-chat-network-prod", "sub-prod"),
        BoundaryTemplate("rg-app", "resource_group", "rg-chat-app-prod", "sub-prod"),
        BoundaryTemplate("rg-ai", "resource_group", "rg-chat-ai-prod", "sub-prod"),
        BoundaryTemplate("rg-data", "resource_group", "rg-chat-data-prod", "sub-prod"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-chat-shared-prod", "sub-prod"),
        BoundaryTemplate("vnet-chat", "vnet", "vnet-chat-prod", "rg-network"),
        BoundaryTemplate("snet-agw", "subnet", "snet-appGateway", "vnet-chat"),
        BoundaryTemplate("snet-app", "subnet", "snet-appServicePlan", "vnet-chat"),
        BoundaryTemplate("snet-pe", "subnet", "snet-privateEndpoints", "vnet-chat"),
        BoundaryTemplate("snet-foundry", "subnet", "snet-foundryIntegration", "vnet-chat"),
        BoundaryTemplate("snet-agent", "subnet", "snet-agentsEgress", "vnet-chat"),
        BoundaryTemplate("snet-bastion", "subnet", "AzureBastionSubnet", "vnet-chat"),
        BoundaryTemplate("snet-jumpbox", "subnet", "snet-jumpBoxes", "vnet-chat"),
        BoundaryTemplate("snet-fw", "subnet", "AzureFirewallSubnet", "vnet-chat"),
    ],

    resources=[
        # Ingress
        ResourceTemplate("application_gateway", "agw1", "Application Gateway + WAF", "snet-agw",
                         {"sku": "WAF_v2", "waf_mode": "Prevention"}),
        ResourceTemplate("ddos_protection", "ddos1", "DDoS Protection", "rg-network"),

        # App tier
        ResourceTemplate("app_service", "app1", "Chat UI (App Service)", "snet-app",
                         {"sku": "P1v3", "zone_redundant": True, "autoscale": True,
                          "availability_zones": "1,2,3"}),
        ResourceTemplate("app_service_plan", "asp1", "App Service Plan", "rg-app"),

        # Private endpoints
        ResourceTemplate("private_endpoint", "pe-foundry", "PE: Foundry", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-cosmos", "PE: Cosmos DB", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-search", "PE: AI Search", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-storage", "PE: Storage", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-kv", "PE: Key Vault", "snet-pe"),

        # AI tier
        ResourceTemplate("openai_service", "oai1", "Azure OpenAI (GPT-4o)", "rg-ai",
                         {"model": "gpt-4o", "deployment_type": "data_zone_provisioned"}),
        ResourceTemplate("ai_search", "search1", "Azure AI Search", "rg-ai",
                         {"sku": "Standard", "replicas": 3}),
        ResourceTemplate("cognitive_services", "foundry1", "Foundry Agent Service", "rg-ai"),

        # Data tier
        ResourceTemplate("cosmos_db", "cosmos1", "Azure Cosmos DB", "rg-data",
                         {"api": "NoSQL", "backup": "continuous", "zone_redundant": True,
                          "geo_replication": True}),
        ResourceTemplate("storage_account", "stor1", "Azure Storage", "rg-data",
                         {"replication": "ZRS"}),

        # Network security
        ResourceTemplate("firewall", "fw1", "Azure Firewall", "snet-fw",
                         {"sku": "Basic"}),
        ResourceTemplate("bastion", "bastion1", "Azure Bastion", "snet-bastion"),
        ResourceTemplate("dns_zone", "dns1", "Private DNS Zones", "rg-network"),
        ResourceTemplate("nsg", "nsg1", "NSGs (per subnet)", "rg-network"),

        # Shared services
        ResourceTemplate("key_vault", "kv1", "Azure Key Vault", "rg-shared"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity (App)", "rg-shared"),
        ResourceTemplate("managed_identity", "mid-foundry", "Managed Identity (Foundry)", "rg-shared"),
        ResourceTemplate("entra_id", "entra1", "Microsoft Entra ID", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-shared"),
        ResourceTemplate("application_insights", "appi1", "Application Insights", "rg-shared"),
        ResourceTemplate("monitor", "mon1", "Azure Monitor", "rg-shared"),
        ResourceTemplate("defender_for_cloud", "defender1", "Defender for Cloud", "rg-shared"),

        # External
        ResourceTemplate("user", "user1", "Chat Users", ""),
    ],

    connections=[
        ConnectionTemplate("user1", "agw1", "HTTPS", "data_flow", workflow_step=1),
        ConnectionTemplate("agw1", "app1", "Internal HTTPS", "data_flow", workflow_step=1),
        ConnectionTemplate("app1", "pe-foundry", "Agent API", "data_flow", workflow_step=2),
        ConnectionTemplate("pe-foundry", "foundry1", "Private Link", "network"),
        ConnectionTemplate("foundry1", "oai1", "Model inference", "data_flow", workflow_step=6),
        ConnectionTemplate("foundry1", "search1", "RAG retrieval", "data_flow", workflow_step=4),
        ConnectionTemplate("foundry1", "cosmos1", "Conversation state", "data_flow", workflow_step=7),
        ConnectionTemplate("foundry1", "stor1", "File storage", "data_flow"),
        ConnectionTemplate("foundry1", "fw1", "Egress (internet tools)", "network", workflow_step=5),
        ConnectionTemplate("app1", "kv1", "TLS certs", "dependency"),
        ConnectionTemplate("app1", "mid1", "Auth", "dependency"),
        ConnectionTemplate("mid-foundry", "entra1", "Token", "dependency"),
        ConnectionTemplate("app1", "appi1", "Telemetry", "dependency"),
        ConnectionTemplate("oai1", "log1", "Diagnostics", "dependency"),
        ConnectionTemplate("search1", "log1", "Diagnostics", "dependency"),
        ConnectionTemplate("pe-cosmos", "cosmos1", "Private Link", "network"),
        ConnectionTemplate("pe-search", "search1", "Private Link", "network"),
        ConnectionTemplate("pe-storage", "stor1", "Private Link", "network"),
        ConnectionTemplate("pe-kv", "kv1", "Private Link", "network"),
    ],

    workflow_steps=[
        WorkflowStep(1, "User sends chat request through Application Gateway with WAF", "user1", "app1"),
        WorkflowStep(2, "App Service invokes Foundry Agent via private endpoint", "app1", "foundry1"),
        WorkflowStep(3, "Agent processes request per system prompt instructions", "foundry1", "foundry1"),
        WorkflowStep(4, "Agent retrieves grounding data from AI Search", "foundry1", "search1"),
        WorkflowStep(5, "External tool calls route through Azure Firewall", "foundry1", "fw1"),
        WorkflowStep(6, "Agent sends context + query to language model", "foundry1", "oai1"),
        WorkflowStep(7, "Agent persists conversation to memory database", "foundry1", "cosmos1"),
    ],

    waf_notes={
        "Reliability": "Zone-redundant App Service, Cosmos DB continuous backup, AI Search 3+ replicas, Firewall across AZs",
        "Security": "Private endpoints for all PaaS, WAF on App Gateway, NSGs per subnet, egress through Firewall, managed identities",
        "Cost Optimization": "Basic Firewall tier, evaluate Cosmos DB reserved capacity, tune AI Search replicas/partitions",
        "Operational Excellence": "Define agents as code, CI/CD deployment, Application Insights + Log Analytics, Defender for Cloud",
        "Performance Efficiency": "Data-zone provisioned model deployment for predictable latency, co-locate resources in same region",
    },

    caf_notes={
        "Naming": "CAF naming: rg-<workload>-<env>-<region>, vnet-<workload>-<env>-<region>",
        "Organization": "Separate RGs per function: network, app, AI, data, shared",
        "Network": "Hub-spoke possible; all traffic through private endpoints; forced tunneling via Firewall",
        "Identity": "Separate managed identities per component (App, Foundry project); Entra ID for user auth",
        "Governance": "Azure Policy to enforce private endpoints, disable key-based auth, restrict regions",
    },

    # ── Layout hints: match Microsoft Architecture Center Foundry Chat diagram ──
    layout_hints={
        # External
        "user1": (1.5, 6),
        # Ingress subnet
        "agw1": (5.5, 5), "ddos1": (5.5, 2.5),
        # App subnet
        "app1": (9, 5), "asp1": (9, 7.5),
        # Private endpoints subnet
        "pe-foundry": (12.5, 3.5), "pe-cosmos": (12.5, 5.5),
        "pe-search": (12.5, 7.5), "pe-storage": (12.5, 9.5), "pe-kv": (12.5, 11.5),
        # AI tier
        "oai1": (16.5, 3.5), "search1": (16.5, 6), "foundry1": (16.5, 8.5),
        # Data tier
        "cosmos1": (20.5, 4), "stor1": (20.5, 7),
        # Network security (bottom of VNet)
        "fw1": (5.5, 13), "bastion1": (8, 13), "dns1": (4, 10.5), "nsg1": (7, 10.5),
        # Shared services (bottom row)
        "kv1": (5, 16), "mid1": (8, 16), "mid-foundry": (11, 16),
        "entra1": (14, 16),
        "log1": (17, 16), "appi1": (20, 16), "mon1": (17, 18), "defender1": (20, 18),
    },
    boundary_hints={
        "sub-prod": (2, 0.5, 22, 19),
        "rg-network": (3, 1.5, 11, 13),
        "rg-app": (7.5, 3.5, 3.5, 5.5),
        "rg-ai": (15, 1.5, 5, 9),
        "rg-data": (19, 1.5, 4.5, 7),
        "rg-shared": (3, 15, 20, 4.5),
        "vnet-chat": (3.5, 2, 10, 12.5),
        "snet-agw": (4, 3, 3.5, 4),
        "snet-app": (7.5, 3, 3.5, 5.5),
        "snet-pe": (11, 2.5, 3.5, 10.5),
        "snet-foundry": (11, 2.5, 3.5, 3),
        "snet-agent": (11, 8.5, 3.5, 3),
        "snet-bastion": (7, 12, 3, 2.5),
        "snet-jumpbox": (10, 12, 3, 2.5),
        "snet-fw": (3.5, 12, 3.5, 2.5),
    },
)


# ═════════════════════════════════════════════════════════════════
# REFERENCE ARCHITECTURE: Azure Landing Zone (Hub-Spoke)
# Source: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/
# ═════════════════════════════════════════════════════════════════

AZURE_LANDING_ZONE = ReferenceArchitecture(
    name="Azure Landing Zone (Hub-Spoke)",
    description=(
        "CAF-aligned enterprise landing zone with management group hierarchy, "
        "platform landing zone (Identity, Management, Connectivity), and "
        "application landing zones. Hub-spoke network topology."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/",
    category="Management + Governance",
    flow_direction="TB",
    layout_strategy="grouped",

    boundaries=[
        # Management group hierarchy
        BoundaryTemplate("mg-root", "management_group", "Contoso (Root MG)"),
        BoundaryTemplate("mg-platform", "management_group", "Platform", "mg-root"),
        BoundaryTemplate("mg-landing", "management_group", "Landing Zones", "mg-root"),
        BoundaryTemplate("mg-decommissioned", "management_group", "Decommissioned", "mg-root"),
        BoundaryTemplate("mg-sandbox", "management_group", "Sandbox", "mg-root"),

        # Platform subscriptions
        BoundaryTemplate("sub-identity", "subscription", "Identity Subscription", "mg-platform"),
        BoundaryTemplate("sub-management", "subscription", "Management Subscription", "mg-platform"),
        BoundaryTemplate("sub-connectivity", "subscription", "Connectivity Subscription", "mg-platform"),

        # Landing zone subscriptions
        BoundaryTemplate("mg-corp", "management_group", "Corp", "mg-landing"),
        BoundaryTemplate("mg-online", "management_group", "Online", "mg-landing"),
        BoundaryTemplate("sub-lz-a", "subscription", "Landing Zone A (Corp)", "mg-corp"),
        BoundaryTemplate("sub-lz-b", "subscription", "Landing Zone B (Online)", "mg-online"),

        # Connectivity VNets
        BoundaryTemplate("vnet-hub", "vnet", "vnet-hub-eastus", "sub-connectivity"),
        BoundaryTemplate("snet-fw", "subnet", "AzureFirewallSubnet", "vnet-hub"),
        BoundaryTemplate("snet-gw", "subnet", "GatewaySubnet", "vnet-hub"),
        BoundaryTemplate("snet-bastion", "subnet", "AzureBastionSubnet", "vnet-hub"),
        BoundaryTemplate("snet-dns", "subnet", "snet-dns-inbound", "vnet-hub"),
        BoundaryTemplate("vnet-spoke-a", "vnet", "vnet-spoke-a-eastus", "sub-lz-a"),
        BoundaryTemplate("vnet-spoke-b", "vnet", "vnet-spoke-b-eastus", "sub-lz-b"),
    ],

    resources=[
        # Connectivity (Hub)
        ResourceTemplate("firewall", "fw1", "Azure Firewall Premium", "snet-fw",
                         {"sku": "Premium", "threat_intel": "Deny",
                          "availability_zones": "1,2,3"}),
        ResourceTemplate("vpn_gateway", "vpngw1", "VPN Gateway", "snet-gw"),
        ResourceTemplate("expressroute", "er1", "ExpressRoute Circuit", "snet-gw"),
        ResourceTemplate("bastion", "bastion1", "Azure Bastion", "snet-bastion"),
        ResourceTemplate("dns_zone", "dns-private", "Private DNS Zones", "snet-dns"),
        ResourceTemplate("ddos_protection", "ddos1", "DDoS Protection Plan", "sub-connectivity"),

        # Identity
        ResourceTemplate("entra_id", "entra1", "Microsoft Entra ID", "sub-identity"),
        ResourceTemplate("managed_identity", "dc1", "Domain Controllers (AD DS)", "sub-identity"),

        # Management
        ResourceTemplate("log_analytics", "log1", "Log Analytics Workspace", "sub-management"),
        ResourceTemplate("monitor", "mon1", "Azure Monitor", "sub-management"),
        ResourceTemplate("policy", "policy1", "Azure Policy", "sub-management"),
        ResourceTemplate("defender_for_cloud", "defender1", "Defender for Cloud", "sub-management"),
        ResourceTemplate("sentinel", "sentinel1", "Microsoft Sentinel", "sub-management"),

        # Landing Zone A (Corp — private, no public inbound)
        ResourceTemplate("virtual_machine", "vm-a1", "Workload VMs", "vnet-spoke-a"),
        ResourceTemplate("sql_database", "sql-a1", "Azure SQL Database", "vnet-spoke-a",
                         {"geo_replication": True, "failover_group": True}),
        ResourceTemplate("private_endpoint", "pe-sql-a1", "PE: SQL Database", "vnet-spoke-a"),
        ResourceTemplate("key_vault", "kv-a1", "Key Vault", "sub-lz-a"),
        ResourceTemplate("nsg", "nsg-a1", "NSGs (per subnet)", "sub-lz-a"),

        # Landing Zone B (Online — public inbound allowed)
        ResourceTemplate("app_service", "app-b1", "App Service", "vnet-spoke-b",
                         {"autoscale": True, "availability_zones": "1,2,3"}),
        ResourceTemplate("application_gateway", "agw-b1", "Application Gateway + WAF", "sub-lz-b"),
        ResourceTemplate("storage_account", "stor-b1", "Storage Account", "sub-lz-b"),
        ResourceTemplate("nsg", "nsg-b1", "NSGs (per subnet)", "sub-lz-b"),

        # External
        ResourceTemplate("on_premises", "onprem1", "On-Premises", ""),
        ResourceTemplate("internet", "inet1", "Internet", ""),
    ],

    connections=[
        # On-prem connectivity
        ConnectionTemplate("onprem1", "vpngw1", "Site-to-Site VPN", "network"),
        ConnectionTemplate("onprem1", "er1", "ExpressRoute", "network"),

        # Hub-spoke peering
        ConnectionTemplate("fw1", "vm-a1", "Spoke A traffic (forced tunnel)", "network"),
        ConnectionTemplate("fw1", "app-b1", "Spoke B traffic (forced tunnel)", "network"),

        # Spoke A flows
        ConnectionTemplate("vm-a1", "sql-a1", "Data access", "data_flow"),
        ConnectionTemplate("vm-a1", "kv-a1", "Secrets", "dependency"),

        # Spoke B flows
        ConnectionTemplate("inet1", "agw-b1", "HTTPS", "data_flow"),
        ConnectionTemplate("agw-b1", "app-b1", "Internal HTTPS", "data_flow"),
        ConnectionTemplate("app-b1", "stor-b1", "Blob access", "data_flow"),

        # Shared services
        ConnectionTemplate("vm-a1", "log1", "Diagnostics", "dependency"),
        ConnectionTemplate("app-b1", "log1", "Diagnostics", "dependency"),
        ConnectionTemplate("fw1", "log1", "Firewall logs", "dependency"),
        ConnectionTemplate("vm-a1", "entra1", "Authentication", "dependency"),
        ConnectionTemplate("app-b1", "entra1", "Authentication", "dependency"),
        ConnectionTemplate("policy1", "sub-lz-a", "Policy enforcement", "reference"),
        ConnectionTemplate("policy1", "sub-lz-b", "Policy enforcement", "reference"),
    ],

    workflow_steps=[
        WorkflowStep(1, "On-premises connects via VPN/ExpressRoute to Hub VNet", "onprem1", "vpngw1"),
        WorkflowStep(2, "All spoke traffic routes through Azure Firewall", "fw1", "vm-a1"),
        WorkflowStep(3, "Internet users reach Online apps via Application Gateway", "inet1", "agw-b1"),
        WorkflowStep(4, "Azure Policy enforces governance across all landing zones", "policy1", "sub-lz-a"),
    ],

    waf_notes={
        "Reliability": "Hub Firewall in all AZs, zone-redundant VPN/ER gateways, spoke workloads across zones",
        "Security": "Forced tunneling through Firewall, private DNS zones, NSG per subnet, DDoS Protection, Defender",
        "Cost Optimization": "Share Firewall + DDoS across landing zones, right-size gateway SKUs",
        "Operational Excellence": "Centralized Log Analytics, Azure Policy at MG scope, Sentinel for SIEM",
        "Performance Efficiency": "Peered VNets for low-latency spoke-to-hub, ExpressRoute for on-prem",
    },

    caf_notes={
        "Naming": "MG hierarchy: Root → Platform/Landing Zones/Sandbox/Decommissioned",
        "Organization": "Separate subscriptions per function: Identity, Management, Connectivity, per-workload LZs",
        "Network": "Hub-spoke with forced tunneling, dedicated subnets per service type",
        "Identity": "Centralized Entra ID in Identity subscription, AD DS DCs if hybrid",
        "Governance": "Policies at Management Group scope, Defender + Sentinel in Management sub",
    },

    # ── Layout hints: match Microsoft Architecture Center Landing Zone diagram ──
    layout_hints={
        # Connectivity Hub
        "fw1": (12, 9), "vpngw1": (9, 9), "er1": (9, 11),
        "bastion1": (15, 9), "dns-private": (15, 11), "ddos1": (12, 7),
        # Identity
        "entra1": (4, 9), "dc1": (4, 11),
        # Management
        "log1": (4, 15), "mon1": (7, 15), "policy1": (10, 15),
        "defender1": (13, 15), "sentinel1": (16, 15),
        # Landing Zone A (Corp)
        "vm-a1": (7, 20), "sql-a1": (10, 20), "pe-sql-a1": (10, 22),
        "kv-a1": (7, 22), "nsg-a1": (13, 22),
        # Landing Zone B (Online)
        "app-b1": (20, 20), "agw-b1": (17, 20), "stor-b1": (23, 20), "nsg-b1": (23, 22),
        # External
        "onprem1": (4, 5), "inet1": (20, 5),
    },
    boundary_hints={
        "mg-root": (1, 1, 27, 24),
        "mg-platform": (2, 2, 17, 4),
        "mg-landing": (2, 17, 25, 8),
        "mg-decommissioned": (20, 2, 4, 4),
        "mg-sandbox": (24, 2, 4, 4),
        "sub-identity": (2.5, 7, 6, 6.5),
        "sub-management": (2.5, 14, 16, 3),
        "sub-connectivity": (9, 6, 9, 7.5),
        "mg-corp": (2.5, 17.5, 14, 7),
        "mg-online": (16.5, 17.5, 10, 7),
        "sub-lz-a": (3, 18, 13, 6),
        "sub-lz-b": (17, 18, 9, 6),
        "vnet-hub": (9.5, 7, 8, 6),
        "snet-fw": (10, 8, 4, 2.5),
        "snet-gw": (10, 10.5, 4, 2),
        "snet-bastion": (14, 8, 3.5, 2.5),
        "snet-dns": (14, 10.5, 3.5, 2),
        "vnet-spoke-a": (4, 19, 11, 4.5),
        "vnet-spoke-b": (18, 19, 7, 4.5),
    },
)


# ═════════════════════════════════════════════════════════════════
# REFERENCE ARCHITECTURE: Baseline Web App (Zone-Redundant)
# Source: https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service/architectures/baseline-zone-redundant
# ═════════════════════════════════════════════════════════════════

BASELINE_WEB_APP = ReferenceArchitecture(
    name="Baseline Zone-Redundant Web Application",
    description=(
        "Zone-redundant web application on App Service with Application Gateway, "
        "private endpoints for all PaaS services, and WAF protection."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/web-apps/app-service/architectures/baseline-zone-redundant",
    category="Web",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "Production Subscription"),
        BoundaryTemplate("rg-network", "resource_group", "rg-webapp-network-prod", "sub-prod"),
        BoundaryTemplate("rg-app", "resource_group", "rg-webapp-app-prod", "sub-prod"),
        BoundaryTemplate("rg-data", "resource_group", "rg-webapp-data-prod", "sub-prod"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-webapp-shared-prod", "sub-prod"),
        BoundaryTemplate("vnet-app", "vnet", "vnet-webapp-prod", "rg-network"),
        BoundaryTemplate("snet-agw", "subnet", "snet-appGateway", "vnet-app"),
        BoundaryTemplate("snet-app", "subnet", "snet-appServiceIntegration", "vnet-app"),
        BoundaryTemplate("snet-pe", "subnet", "snet-privateEndpoints", "vnet-app"),
    ],

    resources=[
        ResourceTemplate("application_gateway", "agw1", "Application Gateway + WAF v2", "snet-agw",
                         {"sku": "WAF_v2", "waf_mode": "Prevention"}),
        ResourceTemplate("ddos_protection", "ddos1", "DDoS Protection", "rg-network"),
        ResourceTemplate("nsg", "nsg1", "NSGs (per subnet)", "rg-network"),
        ResourceTemplate("app_service", "app1", "App Service (zone-redundant)", "snet-app",
                         {"sku": "P1v3", "zone_redundant": True, "autoscale": True,
                          "availability_zones": "1,2,3"}),
        ResourceTemplate("private_endpoint", "pe-sql", "PE: SQL Database", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-kv", "PE: Key Vault", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-stor", "PE: Storage", "snet-pe"),
        ResourceTemplate("sql_database", "sql1", "Azure SQL Database", "rg-data",
                         {"sku": "BusinessCritical", "zone_redundant": True,
                          "geo_replication": True, "failover_group": True}),
        ResourceTemplate("storage_account", "stor1", "Azure Storage", "rg-data",
                         {"replication": "ZRS"}),
        ResourceTemplate("key_vault", "kv1", "Azure Key Vault", "rg-shared"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity", "rg-shared"),
        ResourceTemplate("entra_id", "entra1", "Microsoft Entra ID", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-shared"),
        ResourceTemplate("application_insights", "appi1", "Application Insights", "rg-shared"),
        ResourceTemplate("monitor", "defender1", "Microsoft Defender for Cloud", "rg-shared"),
        ResourceTemplate("user", "user1", "Users", ""),
    ],

    connections=[
        ConnectionTemplate("user1", "agw1", "HTTPS", "data_flow", workflow_step=1),
        ConnectionTemplate("agw1", "app1", "Internal HTTPS", "data_flow", workflow_step=2),
        ConnectionTemplate("app1", "pe-sql", "SQL queries", "data_flow", workflow_step=3),
        ConnectionTemplate("pe-sql", "sql1", "Private Link", "network"),
        ConnectionTemplate("app1", "pe-kv", "Secrets", "dependency"),
        ConnectionTemplate("pe-kv", "kv1", "Private Link", "network"),
        ConnectionTemplate("app1", "pe-stor", "Blob access", "data_flow"),
        ConnectionTemplate("pe-stor", "stor1", "Private Link", "network"),
        ConnectionTemplate("app1", "mid1", "Auth", "dependency"),
        ConnectionTemplate("mid1", "entra1", "Token", "dependency"),
        ConnectionTemplate("app1", "appi1", "Telemetry", "dependency"),
    ],

    workflow_steps=[
        WorkflowStep(1, "User sends HTTPS request to App Gateway with WAF", "user1", "agw1"),
        WorkflowStep(2, "App Gateway routes to App Service via VNet integration", "agw1", "app1"),
        WorkflowStep(3, "App Service accesses PaaS via private endpoints", "app1", "sql1"),
    ],

    waf_notes={
        "Reliability": "Zone-redundant App Service + SQL DB, availability zone spread",
        "Security": "WAF on App Gateway, private endpoints for all PaaS, managed identity, DDoS",
        "Cost Optimization": "Right-size App Service Plan, SQL reserved capacity",
        "Operational Excellence": "App Insights + Log Analytics, deployment slots",
        "Performance Efficiency": "Zone-redundant for low-latency failover",
    },

    caf_notes={
        "Naming": "rg-<workload>-<function>-<env>, vnet-<workload>-<env>",
        "Network": "Single VNet with subnet segmentation, private endpoints in dedicated subnet",
    },

    # ── Layout hints: match Microsoft Architecture Center Baseline Web App diagram ──
    layout_hints={
        # External
        "user1": (1.5, 5.5),
        # Ingress
        "agw1": (5.5, 5), "ddos1": (4, 2.5), "nsg1": (7, 2.5),
        # App tier
        "app1": (9, 5),
        # Private endpoints
        "pe-sql": (12.5, 4), "pe-kv": (12.5, 6), "pe-stor": (12.5, 8),
        # Data tier
        "sql1": (16.5, 4), "stor1": (16.5, 7),
        # Shared services (bottom row)
        "kv1": (5, 11.5), "mid1": (8, 11.5), "entra1": (11, 11.5),
        "log1": (14, 11.5), "appi1": (17, 11.5), "defender1": (20, 11.5),
    },
    boundary_hints={
        "sub-prod": (2.5, 1, 20, 13),
        "rg-network": (3, 1.5, 12, 8.5),
        "rg-app": (8, 3.5, 2.5, 4),
        "rg-data": (15, 1.5, 5, 7),
        "rg-shared": (3.5, 10.5, 18, 3),
        "vnet-app": (3.5, 2, 11, 8),
        "snet-agw": (4, 3.5, 3, 4),
        "snet-app": (7.5, 3.5, 3.5, 4),
        "snet-pe": (11, 3, 3.5, 6.5),
    },
)


# ═════════════════════════════════════════════════════════════════
# REFERENCE ARCHITECTURE: AI Landing Zone in Azure Landing Zone
# Source: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/
# ═════════════════════════════════════════════════════════════════

AI_LANDING_ZONE = ReferenceArchitecture(
    name="AI Workload in Azure Landing Zone",
    description=(
        "AI/ML workload deployed as an application landing zone within the "
        "Azure CAF landing zone architecture. Per Microsoft guidance, AI is "
        "just another workload — no separate AI landing zone is needed."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/",
    category="AI + Machine Learning",
    flow_direction="TB",
    layout_strategy="tiered",

    boundaries=[
        # Platform
        BoundaryTemplate("mg-root", "management_group", "Contoso (Root)"),
        BoundaryTemplate("mg-platform", "management_group", "Platform", "mg-root"),
        BoundaryTemplate("sub-connectivity", "subscription", "Connectivity Subscription", "mg-platform"),
        BoundaryTemplate("sub-management", "subscription", "Management Subscription", "mg-platform"),

        # Landing Zone for AI
        BoundaryTemplate("mg-landing", "management_group", "Landing Zones", "mg-root"),
        BoundaryTemplate("mg-corp", "management_group", "Corp", "mg-landing"),
        BoundaryTemplate("sub-ai", "subscription", "AI Workload Subscription", "mg-corp"),

        # AI subscription internals
        BoundaryTemplate("rg-network", "resource_group", "rg-ai-network-prod-eastus", "sub-ai"),
        BoundaryTemplate("rg-ai", "resource_group", "rg-ai-services-prod-eastus", "sub-ai"),
        BoundaryTemplate("rg-data", "resource_group", "rg-ai-data-prod-eastus", "sub-ai"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-ai-shared-prod-eastus", "sub-ai"),

        BoundaryTemplate("vnet-ai", "vnet", "vnet-ai-spoke-prod-eastus", "rg-network"),
        BoundaryTemplate("snet-agw", "subnet", "snet-appGateway", "vnet-ai"),
        BoundaryTemplate("snet-compute", "subnet", "snet-compute", "vnet-ai"),
        BoundaryTemplate("snet-pe", "subnet", "snet-privateEndpoints", "vnet-ai"),
        BoundaryTemplate("snet-foundry", "subnet", "snet-foundryIntegration", "vnet-ai"),

        # Hub (from platform)
        BoundaryTemplate("vnet-hub", "vnet", "vnet-hub-prod-eastus", "sub-connectivity"),
        BoundaryTemplate("snet-fw", "subnet", "AzureFirewallSubnet", "vnet-hub"),
    ],

    resources=[
        # Hub (shared platform)
        ResourceTemplate("firewall", "fw-hub", "Azure Firewall", "snet-fw",
                         {"sku": "Premium"}),
        ResourceTemplate("vpn_gateway", "vpngw1", "VPN Gateway", "sub-connectivity"),
        ResourceTemplate("log_analytics", "log-plat", "Platform Log Analytics", "sub-management"),
        ResourceTemplate("policy", "policy1", "Azure Policy", "sub-management"),
        ResourceTemplate("defender_for_cloud", "defender1", "Defender for Cloud", "sub-management"),
        ResourceTemplate("sentinel", "sentinel1", "Microsoft Sentinel", "sub-management"),

        # AI spoke — Ingress
        ResourceTemplate("application_gateway", "agw1", "Application Gateway + WAF v2", "snet-agw",
                         {"sku": "WAF_v2"}),
        ResourceTemplate("ddos_protection", "ddos1", "DDoS Protection", "rg-network"),

        # AI spoke — Compute
        ResourceTemplate("container_apps", "ca1", "Container Apps (Inference API)", "snet-compute",
                         {"min_replicas": 2}),
        ResourceTemplate("app_service", "app1", "App Service (Chat UI)", "snet-compute"),

        # AI spoke — AI Services
        ResourceTemplate("openai_service", "oai1", "Azure OpenAI", "rg-ai",
                         {"model": "gpt-4o"}),
        ResourceTemplate("ai_search", "search1", "Azure AI Search", "rg-ai",
                         {"sku": "Standard", "replicas": 3}),
        ResourceTemplate("cognitive_services", "cog1", "Azure AI Services", "rg-ai"),
        ResourceTemplate("machine_learning", "mlw1", "Azure ML Workspace", "rg-ai"),
        ResourceTemplate("container_registry", "cr1", "Container Registry", "rg-ai"),

        # AI spoke — Private endpoints
        ResourceTemplate("private_endpoint", "pe-oai", "PE: OpenAI", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-search", "PE: AI Search", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-cosmos", "PE: Cosmos DB", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-stor", "PE: Storage", "snet-pe"),

        # AI spoke — Data
        ResourceTemplate("cosmos_db", "cosmos1", "Cosmos DB (NoSQL)", "rg-data",
                         {"api": "NoSQL", "zone_redundant": True, "backup": "continuous"}),
        ResourceTemplate("storage_account", "stor1", "Storage Account (GRS)", "rg-data",
                         {"replication": "GRS"}),
        ResourceTemplate("redis_cache", "redis1", "Azure Cache for Redis", "rg-data",
                         {"sku": "Premium"}),

        # AI spoke — Shared
        ResourceTemplate("key_vault", "kv1", "Key Vault", "rg-shared"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity", "rg-shared"),
        ResourceTemplate("entra_id", "entra1", "Microsoft Entra ID", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics (Workload)", "rg-shared"),
        ResourceTemplate("application_insights", "appi1", "Application Insights", "rg-shared"),
        ResourceTemplate("monitor", "mon1", "Azure Monitor", "rg-shared"),

        # External
        ResourceTemplate("user", "user1", "Users / Data Scientists", ""),
        ResourceTemplate("on_premises", "onprem1", "On-Premises", ""),
    ],

    connections=[
        # External ingress
        ConnectionTemplate("user1", "agw1", "HTTPS", "data_flow", workflow_step=1),
        ConnectionTemplate("agw1", "app1", "Internal HTTPS", "data_flow", workflow_step=2),
        ConnectionTemplate("onprem1", "vpngw1", "VPN/ER", "network"),
        ConnectionTemplate("vpngw1", "fw-hub", "Hub routing", "network"),

        # Hub ↔ Spoke
        ConnectionTemplate("fw-hub", "ca1", "Spoke traffic (forced tunnel)", "network"),

        # App → AI
        ConnectionTemplate("app1", "ca1", "API calls", "data_flow", workflow_step=3),
        ConnectionTemplate("ca1", "pe-oai", "OpenAI via PE", "data_flow", workflow_step=4),
        ConnectionTemplate("pe-oai", "oai1", "Private Link", "network"),
        ConnectionTemplate("ca1", "pe-search", "Search via PE", "data_flow"),
        ConnectionTemplate("pe-search", "search1", "Private Link", "network"),
        ConnectionTemplate("oai1", "search1", "RAG retrieval", "data_flow", workflow_step=5),

        # AI → Data
        ConnectionTemplate("search1", "cosmos1", "Index source", "data_flow"),
        ConnectionTemplate("ca1", "pe-cosmos", "Data via PE", "data_flow"),
        ConnectionTemplate("pe-cosmos", "cosmos1", "Private Link", "network"),
        ConnectionTemplate("ca1", "pe-stor", "Storage via PE", "data_flow"),
        ConnectionTemplate("pe-stor", "stor1", "Private Link", "network"),
        ConnectionTemplate("ca1", "redis1", "Cache", "data_flow"),

        # ML
        ConnectionTemplate("mlw1", "cr1", "Model images", "dependency"),
        ConnectionTemplate("mlw1", "oai1", "Fine-tuning", "data_flow"),

        # Shared services
        ConnectionTemplate("ca1", "kv1", "Secrets", "dependency"),
        ConnectionTemplate("ca1", "mid1", "Auth", "dependency"),
        ConnectionTemplate("mid1", "entra1", "Token", "dependency"),
        ConnectionTemplate("ca1", "appi1", "Telemetry", "dependency"),
        ConnectionTemplate("oai1", "log1", "Diagnostics", "dependency"),
        ConnectionTemplate("log1", "log-plat", "Central logging", "reference"),

        # Governance
        ConnectionTemplate("policy1", "sub-ai", "Policy enforcement", "reference"),
        ConnectionTemplate("defender1", "sub-ai", "Security monitoring", "reference"),
    ],

    workflow_steps=[
        WorkflowStep(1, "User accesses chat UI through Application Gateway + WAF", "user1", "agw1"),
        WorkflowStep(2, "App Gateway routes to App Service (Chat UI)", "agw1", "app1"),
        WorkflowStep(3, "Chat UI calls inference API on Container Apps", "app1", "ca1"),
        WorkflowStep(4, "Inference API calls Azure OpenAI via private endpoint", "ca1", "oai1"),
        WorkflowStep(5, "OpenAI retrieves grounding data from AI Search (RAG)", "oai1", "search1"),
        WorkflowStep(6, "All egress traffic flows through hub Firewall", "ca1", "fw-hub"),
    ],

    waf_notes={
        "Reliability": "Zone-redundant compute and data, Cosmos DB continuous backup, AI Search 3 replicas",
        "Security": "Private endpoints everywhere, forced tunneling through hub Firewall, WAF on ingress, Defender + Sentinel",
        "Cost Optimization": "Shared platform Firewall/DDoS, right-size AI Search replicas",
        "Operational Excellence": "Platform + workload Log Analytics, Azure Policy at MG scope, Defender for AI",
        "Performance Efficiency": "Co-locate AI services in same region, provisioned throughput for models",
    },

    caf_notes={
        "Naming": "MG hierarchy, CAF prefixes, environment + region in names",
        "Organization": "AI as application landing zone under Corp MG, shared platform services in Platform subs",
        "Network": "Spoke peered to hub, forced tunneling, dedicated PE subnet",
        "Identity": "Workload managed identity, Entra ID auth, RBAC per project",
        "Governance": "Policy at MG scope, Defender for AI services, Sentinel SIEM",
    },

    # ── Layout hints: match AI Landing Zone in Azure Landing Zone pattern ──
    layout_hints={
        # External
        "user1": (1.5, 8), "onprem1": (1.5, 14),
        # Hub
        "fw-hub": (6, 14), "vpngw1": (6, 16),
        # Platform management
        "log-plat": (20, 3), "policy1": (23, 3), "defender1": (20, 5), "sentinel1": (23, 5),
        # AI Spoke — Ingress
        "agw1": (8, 8), "ddos1": (8, 5.5),
        # AI Spoke — Compute
        "ca1": (12, 8), "app1": (12, 10.5),
        # Private endpoints
        "pe-oai": (16, 7), "pe-search": (16, 9), "pe-cosmos": (16, 11), "pe-stor": (16, 13),
        # AI services
        "oai1": (20, 8), "search1": (20, 10.5), "cog1": (23, 8), "mlw1": (23, 10.5), "cr1": (23, 13),
        # Data
        "cosmos1": (20, 15), "stor1": (23, 15), "redis1": (20, 17),
        # Shared
        "kv1": (8, 19), "mid1": (11, 19), "entra1": (14, 19),
        "log1": (17, 19), "appi1": (20, 19), "mon1": (23, 19),
    },
    boundary_hints={
        "mg-root": (1, 0.5, 26, 21),
        "mg-platform": (2, 1, 8, 5),
        "sub-connectivity": (2, 12, 6, 6),
        "sub-management": (18, 1, 8, 6),
        "mg-landing": (6, 6, 20, 15),
        "mg-corp": (6.5, 6.5, 19, 14),
        "sub-ai": (7, 7, 18, 13),
        "rg-network": (7.5, 7.5, 10, 8),
        "rg-ai": (18, 7, 8, 8),
        "rg-data": (18, 14, 8, 4.5),
        "rg-shared": (7, 18, 18, 2.5),
        "vnet-ai": (8, 7.5, 9, 7.5),
        "snet-agw": (8.5, 8, 2.5, 4),
        "snet-compute": (11, 7.5, 3, 4.5),
        "snet-pe": (14.5, 6.5, 3, 8),
        "snet-foundry": (14.5, 6.5, 3, 3),
        "vnet-hub": (2, 12.5, 5.5, 5),
        "snet-fw": (2.5, 13, 5, 2.5),
    },
)


# ═════════════════════════════════════════════════════════════════
# REFERENCE ARCHITECTURE: Microservices on AKS
# Source: https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices
# ═════════════════════════════════════════════════════════════════

MICROSERVICES_AKS = ReferenceArchitecture(
    name="Microservices on Azure Kubernetes Service",
    description=(
        "Production microservices architecture on AKS with ingress controller, "
        "per-service databases, async messaging, and full observability."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices",
    category="Containers",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "Production Subscription"),
        BoundaryTemplate("rg-aks", "resource_group", "rg-aks-prod-eastus", "sub-prod"),
        BoundaryTemplate("rg-data", "resource_group", "rg-aks-data-prod", "sub-prod"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-aks-shared-prod", "sub-prod"),
        BoundaryTemplate("vnet-aks", "vnet", "vnet-aks-prod-eastus", "rg-aks"),
        BoundaryTemplate("snet-agw", "subnet", "snet-appGateway", "vnet-aks"),
        BoundaryTemplate("snet-aks", "subnet", "snet-aks-nodes", "vnet-aks"),
        BoundaryTemplate("snet-pe", "subnet", "snet-privateEndpoints", "vnet-aks"),
    ],

    resources=[
        ResourceTemplate("front_door", "fd1", "Azure Front Door", "sub-prod"),
        ResourceTemplate("ddos_protection", "ddos1", "DDoS Protection", "sub-prod"),
        ResourceTemplate("application_gateway", "agw1", "Application Gateway (AGIC)", "snet-agw",
                         {"sku": "WAF_v2"}),
        ResourceTemplate("kubernetes_service", "aks1", "AKS Cluster", "snet-aks",
                         {"sku": "Standard", "node_pools": "system + user",
                          "private_cluster": True, "autoscale": True,
                          "availability_zones": "1,2,3"}),
        ResourceTemplate("container_registry", "cr1", "Container Registry", "rg-aks"),
        ResourceTemplate("nsg", "nsg1", "NSGs (per subnet)", "rg-aks"),
        ResourceTemplate("firewall", "fw1", "Azure Firewall (egress)", "rg-aks"),
        ResourceTemplate("private_endpoint", "pe-cr", "PE: ACR", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-cosmos", "PE: Cosmos DB", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-sql", "PE: SQL", "snet-pe"),
        ResourceTemplate("cosmos_db", "cosmos1", "Cosmos DB (Service A)", "rg-data",
                         {"geo_replication": True}),
        ResourceTemplate("sql_database", "sql1", "SQL Database (Service B)", "rg-data",
                         {"geo_replication": True, "failover_group": True}),
        ResourceTemplate("redis_cache", "redis1", "Redis Cache (Shared)", "rg-data"),
        ResourceTemplate("service_bus", "sb1", "Service Bus", "rg-data"),
        ResourceTemplate("event_grid", "eg1", "Event Grid", "rg-data"),
        ResourceTemplate("key_vault", "kv1", "Key Vault", "rg-shared"),
        ResourceTemplate("managed_identity", "mid1", "Workload Identity", "rg-shared"),
        ResourceTemplate("entra_id", "entra1", "Microsoft Entra ID", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-shared"),
        ResourceTemplate("application_insights", "appi1", "Application Insights", "rg-shared"),
        ResourceTemplate("monitor", "mon1", "Azure Monitor + Container Insights", "rg-shared"),
        ResourceTemplate("monitor", "defender1", "Microsoft Defender for Cloud", "rg-shared"),
        ResourceTemplate("user", "user1", "API Consumers", ""),
    ],

    connections=[
        ConnectionTemplate("user1", "fd1", "HTTPS (global)", "data_flow", workflow_step=1),
        ConnectionTemplate("fd1", "agw1", "Regional routing", "data_flow", workflow_step=2),
        ConnectionTemplate("agw1", "aks1", "Ingress to services", "data_flow", workflow_step=3),
        ConnectionTemplate("aks1", "pe-cosmos", "Service A data", "data_flow"),
        ConnectionTemplate("pe-cosmos", "cosmos1", "Private Link", "network"),
        ConnectionTemplate("aks1", "pe-sql", "Service B data", "data_flow"),
        ConnectionTemplate("pe-sql", "sql1", "Private Link", "network"),
        ConnectionTemplate("aks1", "redis1", "Shared cache", "data_flow"),
        ConnectionTemplate("aks1", "sb1", "Async messaging", "data_flow"),
        ConnectionTemplate("sb1", "aks1", "Event processing", "data_flow"),
        ConnectionTemplate("eg1", "aks1", "Event-driven triggers", "data_flow"),
        ConnectionTemplate("aks1", "pe-cr", "Image pull", "dependency"),
        ConnectionTemplate("pe-cr", "cr1", "Private Link", "network"),
        ConnectionTemplate("aks1", "kv1", "Secrets (CSI driver)", "dependency"),
        ConnectionTemplate("aks1", "mid1", "Workload Identity", "dependency"),
        ConnectionTemplate("mid1", "entra1", "Token", "dependency"),
        ConnectionTemplate("aks1", "appi1", "Telemetry", "dependency"),
        ConnectionTemplate("aks1", "log1", "Container Insights", "dependency"),
    ],

    workflow_steps=[
        WorkflowStep(1, "Client sends HTTPS request to Front Door (global LB)", "user1", "fd1"),
        WorkflowStep(2, "Front Door routes to regional Application Gateway", "fd1", "agw1"),
        WorkflowStep(3, "AGIC routes request to appropriate AKS service", "agw1", "aks1"),
        WorkflowStep(4, "Services access per-service databases via private endpoints", "aks1", "cosmos1"),
        WorkflowStep(5, "Async communication via Service Bus", "aks1", "sb1"),
    ],

    waf_notes={
        "Reliability": "Multiple node pools across AZs, PodDisruptionBudgets, zone-redundant databases",
        "Security": "Private AKS cluster, workload identity, network policies, private endpoints, WAF on ingress",
        "Cost Optimization": "Spot node pools for non-critical, cluster autoscaler, right-size nodes",
        "Operational Excellence": "Container Insights, GitOps with Flux, automated upgrades",
        "Performance Efficiency": "HPA + cluster autoscaler, appropriate VM SKUs, Redis for caching",
    },

    caf_notes={
        "Naming": "aks-<workload>-<env>-<region>, per CAF prefix conventions",
        "Network": "Private cluster, AGIC for ingress, dedicated PE subnet",
    },

    # ── Layout hints: match Microsoft Architecture Center Microservices/AKS diagram ──
    layout_hints={
        # External
        "user1": (1.5, 5.5),
        # Edge / Global
        "fd1": (4.5, 5.5), "ddos1": (4.5, 2.5),
        # Ingress
        "agw1": (7.5, 5.5),
        # AKS compute
        "aks1": (11, 5.5), "cr1": (11, 2.5), "nsg1": (8, 9), "fw1": (14, 9),
        # Private endpoints
        "pe-cr": (14, 3.5), "pe-cosmos": (14, 5.5), "pe-sql": (14, 7.5),
        # Data tier
        "cosmos1": (17.5, 4), "sql1": (17.5, 6.5), "redis1": (17.5, 9),
        "sb1": (20.5, 5), "eg1": (20.5, 7.5),
        # Shared services (bottom)
        "kv1": (5, 12.5), "mid1": (8, 12.5), "entra1": (11, 12.5),
        "log1": (14, 12.5), "appi1": (17, 12.5), "mon1": (20, 12.5),
        "defender1": (20, 14.5),
    },
    boundary_hints={
        "sub-prod": (2.5, 1, 21, 15.5),
        "rg-aks": (3, 1.5, 13, 9),
        "rg-data": (16, 1.5, 7, 9),
        "rg-shared": (3.5, 11.5, 19, 4.5),
        "vnet-aks": (3.5, 2, 12, 8),
        "snet-agw": (6, 3.5, 3.5, 4.5),
        "snet-aks": (9.5, 3.5, 3.5, 4.5),
        "snet-pe": (13, 2.5, 2.5, 6.5),
    },
)


# ═════════════════════════════════════════════════════════════════
# NEW REFERENCE ARCHITECTURES (grounded from Azure GitHub org review)
# ═════════════════════════════════════════════════════════════════

# ── Mission-Critical Baseline ─────────────────────────────────────
MISSION_CRITICAL_BASELINE = ReferenceArchitecture(
    name="Mission-Critical Baseline (Multi-Region)",
    description=(
        "Mission-critical workload deployed across multiple active regions with "
        "global load balancing, regional stamps, and health-model-driven failover. "
        "Based on Azure/Mission-Critical GitHub reference."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-mission-critical/mission-critical-intro",
    category="Web",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("global", "management_group", "Global Resources"),
        BoundaryTemplate("stamp-1", "region", "Region 1 – Active Stamp"),
        BoundaryTemplate("rg-stamp1", "resource_group", "rg-mission-stamp1", "stamp-1"),
        BoundaryTemplate("vnet-stamp1", "vnet", "vnet-stamp1", "rg-stamp1"),
        BoundaryTemplate("snet-aks1", "subnet", "snet-aks", "vnet-stamp1"),
        BoundaryTemplate("snet-pe1", "subnet", "snet-privateEndpoints", "vnet-stamp1"),
        BoundaryTemplate("stamp-2", "region", "Region 2 – Active Stamp"),
        BoundaryTemplate("rg-stamp2", "resource_group", "rg-mission-stamp2", "stamp-2"),
        BoundaryTemplate("vnet-stamp2", "vnet", "vnet-stamp2", "rg-stamp2"),
        BoundaryTemplate("snet-aks2", "subnet", "snet-aks", "vnet-stamp2"),
        BoundaryTemplate("snet-pe2", "subnet", "snet-privateEndpoints", "vnet-stamp2"),
        BoundaryTemplate("rg-global", "resource_group", "rg-mission-global", "global"),
    ],

    resources=[
        ResourceTemplate("front_door", "fd1", "Front Door Premium + WAF", "rg-global",
                         {"sku": "Premium", "waf_mode": "Prevention"}),
        ResourceTemplate("cosmos_db", "cosmos-global", "Cosmos DB (multi-region write)", "rg-global",
                         {"multi_region_write": True, "consistency": "Session", "zone_redundant": True}),
        ResourceTemplate("container_registry", "cr-global", "Azure Container Registry (geo-replicated)", "rg-global",
                         {"sku": "Premium", "geo_replication": True}),
        ResourceTemplate("kubernetes_service", "aks1", "AKS Cluster (Region 1)", "snet-aks1",
                         {"sku": "Standard", "availability_zones": "1,2,3", "private_cluster": True}),
        ResourceTemplate("kubernetes_service", "aks2", "AKS Cluster (Region 2)", "snet-aks2",
                         {"sku": "Standard", "availability_zones": "1,2,3", "private_cluster": True}),
        ResourceTemplate("event_hub", "eh1", "Event Hub (health telemetry)", "rg-stamp1"),
        ResourceTemplate("key_vault", "kv1", "Key Vault (Region 1)", "rg-stamp1"),
        ResourceTemplate("key_vault", "kv2", "Key Vault (Region 2)", "rg-stamp2"),
        ResourceTemplate("private_endpoint", "pe-cosmos1", "PE: Cosmos DB (R1)", "snet-pe1"),
        ResourceTemplate("private_endpoint", "pe-cosmos2", "PE: Cosmos DB (R2)", "snet-pe2"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics (central)", "rg-global"),
        ResourceTemplate("application_insights", "appi1", "Application Insights", "rg-global"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity", "rg-global"),
        ResourceTemplate("entra_id", "entra1", "Microsoft Entra ID", "rg-global"),
        ResourceTemplate("user", "user1", "Users", ""),
    ],

    connections=[
        ConnectionTemplate("user1", "fd1", "HTTPS", "data_flow", workflow_step=1),
        ConnectionTemplate("fd1", "aks1", "Route to stamp 1", "data_flow", workflow_step=2),
        ConnectionTemplate("fd1", "aks2", "Route to stamp 2", "data_flow", workflow_step=2),
        ConnectionTemplate("aks1", "pe-cosmos1", "Data queries", "data_flow", workflow_step=3),
        ConnectionTemplate("pe-cosmos1", "cosmos-global", "Private Link", "network"),
        ConnectionTemplate("aks2", "pe-cosmos2", "Data queries", "data_flow"),
        ConnectionTemplate("pe-cosmos2", "cosmos-global", "Private Link", "network"),
        ConnectionTemplate("aks1", "kv1", "Secrets", "dependency"),
        ConnectionTemplate("aks2", "kv2", "Secrets", "dependency"),
        ConnectionTemplate("aks1", "eh1", "Health events", "data_flow"),
        ConnectionTemplate("aks1", "appi1", "Telemetry", "dependency"),
        ConnectionTemplate("aks2", "appi1", "Telemetry", "dependency"),
    ],

    workflow_steps=[
        WorkflowStep(1, "User sends HTTPS request to Front Door (global)", "user1", "fd1"),
        WorkflowStep(2, "Front Door routes to healthy regional stamp based on health model", "fd1", "aks1"),
        WorkflowStep(3, "AKS accesses Cosmos DB via private endpoint (multi-region write)", "aks1", "cosmos-global"),
    ],

    waf_notes={
        "Reliability": "Active-active multi-region stamps; health-model-driven failover; Cosmos multi-region write",
        "Security": "Private AKS clusters; PE for all PaaS; WAF on Front Door; workload identity",
        "Cost Optimization": "Scale stamps independently; use zone-redundant SKUs to avoid over-provisioning",
        "Operational Excellence": "Centralized monitoring; GitOps deployment; automated health checks",
        "Performance Efficiency": "Regional stamps reduce latency; Cosmos DB session consistency",
    },

    caf_notes={
        "Naming": "rg-mission-<stamp>-<env>-<region>",
        "Network": "Isolated VNets per stamp; no VNet peering between stamps; Front Door for global routing",
    },

    layout_hints={
        "user1": (1, 6), "fd1": (4, 6),
        "aks1": (9, 4), "aks2": (9, 8),
        "eh1": (6, 2), "kv1": (12, 2), "kv2": (12, 10),
        "pe-cosmos1": (13, 4), "pe-cosmos2": (13, 8),
        "cosmos-global": (17, 6), "cr-global": (4, 2),
        "log1": (5, 12), "appi1": (8, 12), "mid1": (11, 12), "entra1": (14, 12),
    },
    boundary_hints={
        "global": (2, 0.5, 18, 14),
        "stamp-1": (5.5, 1, 11, 5.5),
        "stamp-2": (5.5, 7, 11, 5.5),
        "rg-stamp1": (6, 1.5, 10, 4.5),
        "rg-stamp2": (6, 7.5, 10, 4.5),
        "vnet-stamp1": (6.5, 2, 9, 3.5),
        "vnet-stamp2": (6.5, 8, 9, 3.5),
        "snet-aks1": (7, 2.5, 4, 2.5),
        "snet-aks2": (7, 8.5, 4, 2.5),
        "snet-pe1": (11.5, 2.5, 3.5, 2.5),
        "snet-pe2": (11.5, 8.5, 3.5, 2.5),
        "rg-global": (3, 11, 14, 3),
    },
)


# ── Container Apps Microservices ──────────────────────────────────
CONTAINER_APPS_MICROSERVICES = ReferenceArchitecture(
    name="Microservices on Azure Container Apps",
    description=(
        "Containerized microservices running on Azure Container Apps with Dapr, "
        "KEDA autoscaling, VNet injection, and private endpoints for backends."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/guide/microservices/azure-container-apps",
    category="Containers",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "Production Subscription"),
        BoundaryTemplate("rg-app", "resource_group", "rg-containerapp-prod", "sub-prod"),
        BoundaryTemplate("rg-data", "resource_group", "rg-containerapp-data-prod", "sub-prod"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-containerapp-shared-prod", "sub-prod"),
        BoundaryTemplate("vnet-app", "vnet", "vnet-containerapp-prod", "rg-app"),
        BoundaryTemplate("snet-cae", "subnet", "snet-containerAppsEnv", "vnet-app"),
        BoundaryTemplate("snet-pe", "subnet", "snet-privateEndpoints", "vnet-app"),
    ],

    resources=[
        ResourceTemplate("application_gateway", "agw1", "Application Gateway + WAF v2", "rg-app",
                         {"sku": "WAF_v2", "waf_mode": "Prevention"}),
        ResourceTemplate("container_apps", "ca-api", "API Service (Container App)", "snet-cae",
                         {"dapr_enabled": True, "autoscale": True, "min_replicas": 1, "max_replicas": 10}),
        ResourceTemplate("container_apps", "ca-worker", "Worker Service (Container App)", "snet-cae",
                         {"dapr_enabled": True, "scale_rule": "service-bus-queue-length"}),
        ResourceTemplate("container_apps", "ca-web", "Web Frontend (Container App)", "snet-cae",
                         {"dapr_enabled": True, "autoscale": True}),
        ResourceTemplate("container_registry", "cr1", "Azure Container Registry", "rg-shared",
                         {"sku": "Premium"}),
        ResourceTemplate("service_bus", "sb1", "Service Bus", "rg-data"),
        ResourceTemplate("cosmos_db", "cosmos1", "Cosmos DB", "rg-data",
                         {"consistency": "Session", "zone_redundant": True}),
        ResourceTemplate("redis_cache", "redis1", "Azure Cache for Redis", "rg-data"),
        ResourceTemplate("private_endpoint", "pe-cosmos", "PE: Cosmos DB", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-sb", "PE: Service Bus", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-redis", "PE: Redis", "snet-pe"),
        ResourceTemplate("key_vault", "kv1", "Key Vault", "rg-shared"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-shared"),
        ResourceTemplate("application_insights", "appi1", "Application Insights", "rg-shared"),
        ResourceTemplate("user", "user1", "Users", ""),
    ],

    connections=[
        ConnectionTemplate("user1", "agw1", "HTTPS", "data_flow", workflow_step=1),
        ConnectionTemplate("agw1", "ca-web", "Route to frontend", "data_flow", workflow_step=2),
        ConnectionTemplate("ca-web", "ca-api", "Dapr service invoke", "data_flow", workflow_step=3),
        ConnectionTemplate("ca-api", "pe-cosmos", "Data queries (Dapr state)", "data_flow", workflow_step=4),
        ConnectionTemplate("pe-cosmos", "cosmos1", "Private Link", "network"),
        ConnectionTemplate("ca-api", "pe-sb", "Async messages", "data_flow"),
        ConnectionTemplate("pe-sb", "sb1", "Private Link", "network"),
        ConnectionTemplate("ca-worker", "pe-sb", "Process messages (KEDA)", "data_flow"),
        ConnectionTemplate("ca-api", "pe-redis", "Cache", "data_flow"),
        ConnectionTemplate("pe-redis", "redis1", "Private Link", "network"),
        ConnectionTemplate("ca-api", "kv1", "Secrets (Dapr)", "dependency"),
        ConnectionTemplate("ca-api", "appi1", "Telemetry", "dependency"),
    ],

    workflow_steps=[
        WorkflowStep(1, "User sends HTTPS to Application Gateway with WAF", "user1", "agw1"),
        WorkflowStep(2, "App Gateway routes to Container Apps web frontend", "agw1", "ca-web"),
        WorkflowStep(3, "Frontend calls API via Dapr service invocation", "ca-web", "ca-api"),
        WorkflowStep(4, "API queries Cosmos DB via private endpoint (Dapr state store)", "ca-api", "cosmos1"),
    ],

    waf_notes={
        "Reliability": "KEDA autoscaling, zone-redundant Cosmos DB, Dapr retry policies",
        "Security": "VNet-injected Container Apps env, WAF on ingress, PE for all PaaS, managed identity",
        "Cost Optimization": "Consumption plan for bursty workloads; KEDA scales to zero for workers",
        "Operational Excellence": "Dapr for service mesh, Container Insights, revision management",
        "Performance Efficiency": "KEDA event-driven scaling, Redis caching, Dapr pub/sub",
    },

    caf_notes={
        "Naming": "ca-<service>-<env>-<region>, rg-containerapp-<function>-<env>",
        "Network": "VNet-injected environment, dedicated PE subnet",
    },

    layout_hints={
        "user1": (1, 5), "agw1": (4, 5),
        "ca-web": (7.5, 3.5), "ca-api": (7.5, 5.5), "ca-worker": (7.5, 7.5),
        "cr1": (4.5, 1),
        "pe-cosmos": (11, 4), "pe-sb": (11, 6), "pe-redis": (11, 8),
        "cosmos1": (15, 4), "sb1": (15, 6), "redis1": (15, 8),
        "kv1": (5, 11), "mid1": (8, 11), "log1": (11, 11), "appi1": (14, 11),
    },
    boundary_hints={
        "sub-prod": (2, 0.5, 17, 12),
        "rg-app": (3, 1, 10, 8),
        "rg-data": (13.5, 1, 5, 8),
        "rg-shared": (3.5, 10, 13, 3),
        "vnet-app": (3.5, 1.5, 9, 7),
        "snet-cae": (5.5, 2, 4, 7),
        "snet-pe": (10, 2, 3, 7),
    },
)


# ── IaaS Baseline (N-Tier) ───────────────────────────────────────
IAAS_BASELINE = ReferenceArchitecture(
    name="IaaS N-Tier Baseline",
    description=(
        "Traditional N-tier application on VMs with load balancers, "
        "Availability Zones, NSGs per tier, and Bastion for secure access."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/n-tier/n-tier-sql-server",
    category="Compute",
    flow_direction="TB",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "Production Subscription"),
        BoundaryTemplate("rg-ntier", "resource_group", "rg-ntier-prod", "sub-prod"),
        BoundaryTemplate("vnet-ntier", "vnet", "vnet-ntier-prod", "rg-ntier"),
        BoundaryTemplate("snet-web", "subnet", "snet-web-tier", "vnet-ntier"),
        BoundaryTemplate("snet-biz", "subnet", "snet-business-tier", "vnet-ntier"),
        BoundaryTemplate("snet-data", "subnet", "snet-data-tier", "vnet-ntier"),
        BoundaryTemplate("snet-mgmt", "subnet", "snet-management", "vnet-ntier"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-ntier-shared-prod", "sub-prod"),
    ],

    resources=[
        ResourceTemplate("application_gateway", "agw1", "Application Gateway + WAF v2", "snet-web",
                         {"sku": "WAF_v2", "waf_mode": "Prevention"}),
        ResourceTemplate("vm_scale_set", "vmss-web", "Web Tier VMSS", "snet-web",
                         {"availability_zones": "1,2,3", "autoscale": True}),
        ResourceTemplate("load_balancer", "lb-biz", "Internal Load Balancer", "snet-biz"),
        ResourceTemplate("vm_scale_set", "vmss-biz", "Business Tier VMSS", "snet-biz",
                         {"availability_zones": "1,2,3", "autoscale": True}),
        ResourceTemplate("load_balancer", "lb-data", "Internal Load Balancer", "snet-data"),
        ResourceTemplate("virtual_machine", "sql-primary", "SQL Server (Primary)", "snet-data",
                         {"availability_zone": "1"}),
        ResourceTemplate("virtual_machine", "sql-secondary", "SQL Server (Secondary)", "snet-data",
                         {"availability_zone": "2"}),
        ResourceTemplate("nsg", "nsg-web", "NSG: Web Tier", "snet-web"),
        ResourceTemplate("nsg", "nsg-biz", "NSG: Business Tier", "snet-biz"),
        ResourceTemplate("nsg", "nsg-data", "NSG: Data Tier", "snet-data"),
        ResourceTemplate("bastion", "bas1", "Azure Bastion", "snet-mgmt"),
        ResourceTemplate("key_vault", "kv1", "Key Vault", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-shared"),
        ResourceTemplate("recovery_services_vault", "rsv1", "Recovery Services Vault", "rg-shared"),
        ResourceTemplate("user", "user1", "Users", ""),
    ],

    connections=[
        ConnectionTemplate("user1", "agw1", "HTTPS", "data_flow", workflow_step=1),
        ConnectionTemplate("agw1", "vmss-web", "HTTP to web farm", "data_flow", workflow_step=2),
        ConnectionTemplate("vmss-web", "lb-biz", "Business logic calls", "data_flow", workflow_step=3),
        ConnectionTemplate("lb-biz", "vmss-biz", "Load-balanced requests", "data_flow"),
        ConnectionTemplate("vmss-biz", "lb-data", "Data access", "data_flow", workflow_step=4),
        ConnectionTemplate("lb-data", "sql-primary", "SQL queries", "data_flow"),
        ConnectionTemplate("sql-primary", "sql-secondary", "Always-On replication", "network"),
        ConnectionTemplate("bas1", "vmss-web", "Admin RDP/SSH", "dependency"),
        ConnectionTemplate("vmss-web", "log1", "Diagnostics", "dependency"),
    ],

    workflow_steps=[
        WorkflowStep(1, "User accesses web app via Application Gateway with WAF", "user1", "agw1"),
        WorkflowStep(2, "App Gateway routes to web-tier VMSS", "agw1", "vmss-web"),
        WorkflowStep(3, "Web tier calls business tier via internal load balancer", "vmss-web", "vmss-biz"),
        WorkflowStep(4, "Business tier accesses SQL Server Always-On via internal LB", "vmss-biz", "sql-primary"),
    ],

    waf_notes={
        "Reliability": "VMSS across AZs per tier, SQL Always-On, Recovery Services Vault",
        "Security": "WAF on ingress, NSG per subnet, Bastion for admin, no public IPs on VMs",
        "Cost Optimization": "Right-size VMSS, Reserved Instances for predictable workloads",
        "Operational Excellence": "Centralized logging, Azure Backup via RSV, VMSS auto-updates",
        "Performance Efficiency": "Autoscale per tier, Accelerated Networking on VMs",
    },

    caf_notes={
        "Naming": "vmss-<tier>-<env>, snet-<tier>",
        "Network": "Subnet per tier with NSG isolation",
    },

    layout_hints={
        "user1": (8.5, 1),
        "agw1": (8.5, 3.5), "nsg-web": (5, 4),
        "vmss-web": (8.5, 5.5),
        "lb-biz": (8.5, 7.5), "nsg-biz": (5, 8),
        "vmss-biz": (8.5, 9.5),
        "lb-data": (8.5, 11.5), "nsg-data": (5, 12),
        "sql-primary": (7.5, 13.5), "sql-secondary": (10, 13.5),
        "bas1": (14, 5),
        "kv1": (3, 15), "log1": (6, 15), "rsv1": (9, 15),
    },
    boundary_hints={
        "sub-prod": (2, 0.5, 15, 16),
        "rg-ntier": (2.5, 1, 12, 14),
        "vnet-ntier": (3, 1.5, 11, 13),
        "snet-web": (4, 2.5, 8, 4),
        "snet-biz": (4, 7, 8, 4),
        "snet-data": (4, 11.5, 8, 3),
        "snet-mgmt": (12.5, 3.5, 3, 4),
        "rg-shared": (2.5, 14.5, 10, 2),
    },
)


# ── App Service Environment (ASE) ────────────────────────────────
APP_SERVICE_ASE = ReferenceArchitecture(
    name="App Service Environment (ASE v3) with Private Networking",
    description=(
        "Fully isolated, dedicated App Service Environment v3 for "
        "compliance-critical workloads. VNet-injected with private endpoint "
        "access to backend services and WAF on ingress."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/enterprise-integration/ase-high-availability-deployment",
    category="Web",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "Production Subscription"),
        BoundaryTemplate("rg-ase", "resource_group", "rg-ase-prod", "sub-prod"),
        BoundaryTemplate("vnet-ase", "vnet", "vnet-ase-prod", "rg-ase"),
        BoundaryTemplate("snet-agw", "subnet", "snet-appGateway", "vnet-ase"),
        BoundaryTemplate("snet-ase", "subnet", "snet-aseInternal", "vnet-ase"),
        BoundaryTemplate("snet-pe", "subnet", "snet-privateEndpoints", "vnet-ase"),
        BoundaryTemplate("rg-data", "resource_group", "rg-ase-data-prod", "sub-prod"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-ase-shared-prod", "sub-prod"),
    ],

    resources=[
        ResourceTemplate("application_gateway", "agw1", "Application Gateway WAF v2", "snet-agw",
                         {"sku": "WAF_v2", "waf_mode": "Prevention"}),
        ResourceTemplate("app_service", "ase-app", "App Service on ASE v3", "snet-ase",
                         {"ase_v3": True, "zone_redundant": True, "internal_only": True}),
        ResourceTemplate("app_service_plan", "asp-ase", "ASE Plan (Isolated v2)", "snet-ase",
                         {"sku": "I1v2"}),
        ResourceTemplate("sql_database", "sql1", "Azure SQL Database", "rg-data",
                         {"sku": "BusinessCritical", "zone_redundant": True}),
        ResourceTemplate("storage_account", "stor1", "Storage Account", "rg-data"),
        ResourceTemplate("private_endpoint", "pe-sql", "PE: SQL Database", "snet-pe"),
        ResourceTemplate("private_endpoint", "pe-stor", "PE: Storage", "snet-pe"),
        ResourceTemplate("key_vault", "kv1", "Key Vault", "rg-shared"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-shared"),
        ResourceTemplate("application_insights", "appi1", "Application Insights", "rg-shared"),
        ResourceTemplate("user", "user1", "Users", ""),
    ],

    connections=[
        ConnectionTemplate("user1", "agw1", "HTTPS", "data_flow", workflow_step=1),
        ConnectionTemplate("agw1", "ase-app", "Internal VIP routing", "data_flow", workflow_step=2),
        ConnectionTemplate("ase-app", "pe-sql", "SQL queries", "data_flow", workflow_step=3),
        ConnectionTemplate("pe-sql", "sql1", "Private Link", "network"),
        ConnectionTemplate("ase-app", "pe-stor", "Blob access", "data_flow"),
        ConnectionTemplate("pe-stor", "stor1", "Private Link", "network"),
        ConnectionTemplate("ase-app", "kv1", "Secrets", "dependency"),
        ConnectionTemplate("ase-app", "appi1", "Telemetry", "dependency"),
    ],

    workflow_steps=[
        WorkflowStep(1, "User sends HTTPS to App Gateway WAF", "user1", "agw1"),
        WorkflowStep(2, "App Gateway routes to internal ASE v3 VIP", "agw1", "ase-app"),
        WorkflowStep(3, "App accesses SQL via private endpoint", "ase-app", "sql1"),
    ],

    waf_notes={
        "Reliability": "Zone-redundant ASE v3 + SQL Business Critical in AZs",
        "Security": "Fully isolated environment; internal-only VIP; WAF on all ingress; PE for data",
        "Cost Optimization": "ASE v3 is cheaper than v2; use reserved instances for Isolated v2 plans",
        "Operational Excellence": "Deployment slots for zero-downtime; App Insights + Log Analytics",
        "Performance Efficiency": "Dedicated compute environment removes noisy-neighbor risk",
    },

    caf_notes={
        "Naming": "ase-<workload>-<env>, rg-ase-<function>-<env>",
        "Network": "Internal ASE in dedicated subnet (minimum /24); PE in separate subnet",
    },

    layout_hints={
        "user1": (1, 5), "agw1": (4.5, 5),
        "ase-app": (8.5, 5), "asp-ase": (8.5, 2.5),
        "pe-sql": (12, 4), "pe-stor": (12, 6.5),
        "sql1": (16, 4), "stor1": (16, 6.5),
        "kv1": (5, 10), "mid1": (8, 10), "log1": (11, 10), "appi1": (14, 10),
    },
    boundary_hints={
        "sub-prod": (2, 0.5, 16, 11),
        "rg-ase": (2.5, 1, 11, 7.5),
        "rg-data": (14, 1, 5, 7.5),
        "rg-shared": (3, 9, 13, 2.5),
        "vnet-ase": (3, 1.5, 10, 6.5),
        "snet-agw": (3.5, 3, 3, 4.5),
        "snet-ase": (7, 1.5, 4, 5),
        "snet-pe": (11, 2.5, 2.5, 5),
    },
)


# ── Data Analytics – Medallion Architecture ───────────────────────
DATA_ANALYTICS_MEDALLION = ReferenceArchitecture(
    name="Data Analytics Platform – Medallion Architecture",
    description=(
        "Lakehouse-style analytics platform with Bronze/Silver/Gold layers "
        "using Azure Databricks and Data Lake Storage Gen2. Includes ingestion "
        "via Data Factory and governance via Purview."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/azure-databricks-modern-analytics-architecture",
    category="Analytics",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "Analytics Subscription"),
        BoundaryTemplate("rg-ingest", "resource_group", "rg-analytics-ingest-prod", "sub-prod"),
        BoundaryTemplate("rg-process", "resource_group", "rg-analytics-process-prod", "sub-prod"),
        BoundaryTemplate("rg-serve", "resource_group", "rg-analytics-serve-prod", "sub-prod"),
        BoundaryTemplate("rg-govern", "resource_group", "rg-analytics-govern-prod", "sub-prod"),
    ],

    resources=[
        # Ingestion
        ResourceTemplate("data_factory", "adf1", "Azure Data Factory", "rg-ingest"),
        ResourceTemplate("event_hub", "eh1", "Event Hub (streaming)", "rg-ingest"),
        # Processing (Medallion layers)
        ResourceTemplate("data_lake_storage", "adls-bronze", "ADLS Gen2 (Bronze – Raw)", "rg-process",
                         {"hierarchical_namespace": True, "replication": "ZRS"}),
        ResourceTemplate("data_lake_storage", "adls-silver", "ADLS Gen2 (Silver – Cleansed)", "rg-process",
                         {"hierarchical_namespace": True, "replication": "ZRS"}),
        ResourceTemplate("data_lake_storage", "adls-gold", "ADLS Gen2 (Gold – Curated)", "rg-process",
                         {"hierarchical_namespace": True, "replication": "ZRS"}),
        ResourceTemplate("databricks", "dbw1", "Azure Databricks", "rg-process"),
        # Serving
        ResourceTemplate("synapse_analytics", "syn1", "Synapse Analytics (Serverless SQL)", "rg-serve"),
        ResourceTemplate("cosmos_db", "cosmos1", "Cosmos DB (serving layer)", "rg-serve",
                         {"consistency": "Session"}),
        # Governance
        ResourceTemplate("purview", "purview1", "Microsoft Purview", "rg-govern"),
        ResourceTemplate("key_vault", "kv1", "Key Vault", "rg-govern"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-govern"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity", "rg-govern"),
        # External
        ResourceTemplate("on_premises", "source1", "On-premises / External Sources", ""),
        ResourceTemplate("user", "analyst1", "Data Analysts", ""),
    ],

    connections=[
        ConnectionTemplate("source1", "adf1", "Batch ingestion", "data_flow", workflow_step=1),
        ConnectionTemplate("source1", "eh1", "Streaming data", "data_flow", workflow_step=1),
        ConnectionTemplate("adf1", "adls-bronze", "Raw data landing", "data_flow", workflow_step=2),
        ConnectionTemplate("eh1", "adls-bronze", "Stream capture", "data_flow", workflow_step=2),
        ConnectionTemplate("dbw1", "adls-bronze", "Read raw data", "data_flow", workflow_step=3),
        ConnectionTemplate("dbw1", "adls-silver", "Write cleansed data", "data_flow", workflow_step=3),
        ConnectionTemplate("dbw1", "adls-gold", "Write curated aggregates", "data_flow", workflow_step=4),
        ConnectionTemplate("syn1", "adls-gold", "Query gold layer", "data_flow", workflow_step=5),
        ConnectionTemplate("cosmos1", "adls-gold", "Serve curated data", "data_flow"),
        ConnectionTemplate("analyst1", "syn1", "BI queries", "data_flow", workflow_step=5),
        ConnectionTemplate("purview1", "adls-bronze", "Scan & catalog", "dependency"),
        ConnectionTemplate("purview1", "adls-silver", "Scan & catalog", "dependency"),
        ConnectionTemplate("purview1", "adls-gold", "Scan & catalog", "dependency"),
    ],

    workflow_steps=[
        WorkflowStep(1, "Data ingested from sources via Data Factory (batch) and Event Hub (stream)", "source1", "adf1"),
        WorkflowStep(2, "Raw data lands in Bronze layer (ADLS Gen2)", "adf1", "adls-bronze"),
        WorkflowStep(3, "Databricks cleanses and conforms data → Silver layer", "dbw1", "adls-silver"),
        WorkflowStep(4, "Databricks aggregates business metrics → Gold layer", "dbw1", "adls-gold"),
        WorkflowStep(5, "Analysts query Gold via Synapse Serverless SQL", "analyst1", "syn1"),
    ],

    waf_notes={
        "Reliability": "ZRS for all ADLS accounts; Databricks cluster auto-recovery",
        "Security": "Private endpoints for ADLS/Synapse; managed identity; Purview classification",
        "Cost Optimization": "Serverless SQL pools (pay-per-query); Databricks spot instances; lifecycle policies on Bronze",
        "Operational Excellence": "Purview for data lineage; centralized logging; CI/CD for notebooks",
        "Performance Efficiency": "Delta Lake format for reads; partitioning strategy per layer",
    },

    caf_notes={
        "Naming": "adls<layer><env><region>, dbw-<workload>-<env>",
        "Network": "Private endpoints for all data services",
    },

    layout_hints={
        "source1": (1, 5), "adf1": (4, 3.5), "eh1": (4, 6.5),
        "adls-bronze": (8, 5), "dbw1": (11, 5),
        "adls-silver": (14, 3.5), "adls-gold": (14, 6.5),
        "syn1": (18, 4), "cosmos1": (18, 7), "analyst1": (22, 5),
        "purview1": (11, 10), "kv1": (5, 10), "log1": (8, 10), "mid1": (14, 10),
    },
    boundary_hints={
        "sub-prod": (2, 0.5, 22, 11.5),
        "rg-ingest": (2.5, 1, 4, 7.5),
        "rg-process": (7, 1, 9.5, 7.5),
        "rg-serve": (17, 1, 5, 7.5),
        "rg-govern": (3.5, 9, 13, 3),
    },
)


# ── Serverless Event-Driven ──────────────────────────────────────
SERVERLESS_EVENT_DRIVEN = ReferenceArchitecture(
    name="Serverless Event-Driven Architecture",
    description=(
        "Event-driven, serverless architecture using Azure Functions, Event Grid, "
        "Service Bus, and Cosmos DB. No server management, pay-per-execution."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/serverless/event-processing",
    category="Serverless",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "Production Subscription"),
        BoundaryTemplate("rg-func", "resource_group", "rg-serverless-func-prod", "sub-prod"),
        BoundaryTemplate("rg-data", "resource_group", "rg-serverless-data-prod", "sub-prod"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-serverless-shared-prod", "sub-prod"),
    ],

    resources=[
        ResourceTemplate("api_management", "apim1", "API Management (Consumption)", "rg-func",
                         {"sku": "Consumption"}),
        ResourceTemplate("function_app", "func-api", "API Functions", "rg-func",
                         {"runtime": "dotnet-isolated", "plan": "Consumption"}),
        ResourceTemplate("function_app", "func-processor", "Event Processor Functions", "rg-func",
                         {"runtime": "dotnet-isolated", "plan": "Consumption"}),
        ResourceTemplate("event_grid", "eg1", "Event Grid Topic", "rg-func"),
        ResourceTemplate("service_bus", "sb1", "Service Bus (dead-letter + retry)", "rg-data"),
        ResourceTemplate("cosmos_db", "cosmos1", "Cosmos DB (event store)", "rg-data",
                         {"consistency": "Session", "zone_redundant": True}),
        ResourceTemplate("storage_account", "stor1", "Storage Account (function state)", "rg-data"),
        ResourceTemplate("key_vault", "kv1", "Key Vault", "rg-shared"),
        ResourceTemplate("application_insights", "appi1", "Application Insights", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-shared"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity", "rg-shared"),
        ResourceTemplate("user", "user1", "Users / External Systems", ""),
    ],

    connections=[
        ConnectionTemplate("user1", "apim1", "HTTPS API call", "data_flow", workflow_step=1),
        ConnectionTemplate("apim1", "func-api", "Route to function", "data_flow", workflow_step=2),
        ConnectionTemplate("func-api", "eg1", "Publish event", "data_flow", workflow_step=3),
        ConnectionTemplate("eg1", "func-processor", "Event Grid trigger", "data_flow", workflow_step=4),
        ConnectionTemplate("func-processor", "cosmos1", "Write event data", "data_flow", workflow_step=5),
        ConnectionTemplate("func-processor", "sb1", "Dead-letter / retry", "data_flow"),
        ConnectionTemplate("func-api", "stor1", "Function state", "dependency"),
        ConnectionTemplate("func-api", "kv1", "Secrets", "dependency"),
        ConnectionTemplate("func-api", "appi1", "Telemetry", "dependency"),
    ],

    workflow_steps=[
        WorkflowStep(1, "Client calls API via API Management", "user1", "apim1"),
        WorkflowStep(2, "APIM routes to API Functions", "apim1", "func-api"),
        WorkflowStep(3, "Function publishes event to Event Grid", "func-api", "eg1"),
        WorkflowStep(4, "Event Grid triggers processor function", "eg1", "func-processor"),
        WorkflowStep(5, "Processor writes to Cosmos DB", "func-processor", "cosmos1"),
    ],

    waf_notes={
        "Reliability": "Event Grid guaranteed delivery; Service Bus dead-letter; Cosmos multi-region",
        "Security": "APIM for API gateway security; managed identity; private endpoints",
        "Cost Optimization": "Consumption plan – pay only for executions; no idle compute",
        "Operational Excellence": "Application Insights distributed tracing; deployment slots",
        "Performance Efficiency": "Event-driven auto-scale; Cosmos DB request units auto-scale",
    },

    caf_notes={
        "Naming": "func-<purpose>-<env>, eg-<topic>-<env>",
        "Network": "Consider VNet integration for premium Functions plan in production",
    },

    layout_hints={
        "user1": (1, 5), "apim1": (4, 5),
        "func-api": (7.5, 5), "eg1": (11, 5),
        "func-processor": (14.5, 5),
        "cosmos1": (18, 3.5), "sb1": (18, 6.5), "stor1": (7.5, 2),
        "kv1": (5, 9), "appi1": (8, 9), "log1": (11, 9), "mid1": (14, 9),
    },
    boundary_hints={
        "sub-prod": (2, 0.5, 19, 10),
        "rg-func": (2.5, 1, 14, 6.5),
        "rg-data": (16.5, 1, 5, 6.5),
        "rg-shared": (3, 8, 13, 2.5),
    },
)


# ── IoT Reference Architecture ───────────────────────────────────
IOT_REFERENCE = ReferenceArchitecture(
    name="IoT Reference Architecture",
    description=(
        "End-to-end IoT solution with device provisioning, telemetry ingestion, "
        "stream processing, warm/cold path analytics, and device management."
    ),
    source_url="https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/iot",
    category="IoT",
    flow_direction="LR",
    layout_strategy="tiered",

    boundaries=[
        BoundaryTemplate("sub-prod", "subscription", "IoT Subscription"),
        BoundaryTemplate("rg-iot", "resource_group", "rg-iot-prod", "sub-prod"),
        BoundaryTemplate("rg-analytics", "resource_group", "rg-iot-analytics-prod", "sub-prod"),
        BoundaryTemplate("rg-shared", "resource_group", "rg-iot-shared-prod", "sub-prod"),
    ],

    resources=[
        ResourceTemplate("iot_hub", "iot1", "Azure IoT Hub", "rg-iot",
                         {"sku": "S1", "partitions": 4}),
        ResourceTemplate("iot_edge", "edge1", "IoT Edge (gateway)", ""),
        ResourceTemplate("stream_analytics", "asa1", "Stream Analytics (hot path)", "rg-analytics"),
        ResourceTemplate("data_lake_storage", "adls1", "ADLS Gen2 (cold path)", "rg-analytics",
                         {"hierarchical_namespace": True}),
        ResourceTemplate("cosmos_db", "cosmos1", "Cosmos DB (warm path)", "rg-analytics",
                         {"consistency": "Session"}),
        ResourceTemplate("event_hub", "eh1", "Event Hub (routing)", "rg-iot"),
        ResourceTemplate("function_app", "func1", "Functions (device commands)", "rg-iot"),
        ResourceTemplate("databricks", "dbw1", "Databricks (batch analytics)", "rg-analytics"),
        ResourceTemplate("time_series_insights", "tsi1", "Time Series Insights", "rg-analytics"),
        ResourceTemplate("key_vault", "kv1", "Key Vault", "rg-shared"),
        ResourceTemplate("log_analytics", "log1", "Log Analytics", "rg-shared"),
        ResourceTemplate("managed_identity", "mid1", "Managed Identity", "rg-shared"),
        ResourceTemplate("user", "operator1", "IoT Operators / Dashboard", ""),
    ],

    connections=[
        ConnectionTemplate("edge1", "iot1", "Device telemetry (MQTT/AMQP)", "data_flow", workflow_step=1),
        ConnectionTemplate("iot1", "eh1", "Message routing", "data_flow", workflow_step=2),
        ConnectionTemplate("eh1", "asa1", "Hot path stream", "data_flow", workflow_step=3),
        ConnectionTemplate("asa1", "cosmos1", "Real-time aggregates", "data_flow", workflow_step=4),
        ConnectionTemplate("eh1", "adls1", "Cold path capture", "data_flow"),
        ConnectionTemplate("adls1", "dbw1", "Batch processing", "data_flow"),
        ConnectionTemplate("iot1", "func1", "Device commands", "data_flow"),
        ConnectionTemplate("cosmos1", "tsi1", "Time series exploration", "data_flow"),
        ConnectionTemplate("operator1", "tsi1", "Visualization", "data_flow", workflow_step=5),
    ],

    workflow_steps=[
        WorkflowStep(1, "IoT Edge devices send telemetry to IoT Hub", "edge1", "iot1"),
        WorkflowStep(2, "IoT Hub routes messages to Event Hub", "iot1", "eh1"),
        WorkflowStep(3, "Stream Analytics processes hot path in real-time", "eh1", "asa1"),
        WorkflowStep(4, "Aggregates written to Cosmos DB warm store", "asa1", "cosmos1"),
        WorkflowStep(5, "Operators view dashboards via Time Series Insights", "operator1", "tsi1"),
    ],

    waf_notes={
        "Reliability": "IoT Hub partitions for throughput; Cosmos multi-region; ADLS ZRS",
        "Security": "Device provisioning with X.509 certs; managed identity; private endpoints",
        "Cost Optimization": "Stream Analytics SU right-sizing; cold path in ADLS for infrequent access",
        "Operational Excellence": "IoT Hub diagnostics → Log Analytics; device twin for config",
        "Performance Efficiency": "Event Hub partitions aligned with Stream Analytics; Cosmos RU autoscale",
    },

    caf_notes={
        "Naming": "iot-<workload>-<env>, asa-<purpose>-<env>",
        "Network": "VNet service endpoints or PE for IoT Hub (premium) and Cosmos DB",
    },

    layout_hints={
        "edge1": (1, 5), "iot1": (5, 5),
        "eh1": (9, 5), "func1": (5, 2),
        "asa1": (12.5, 3.5), "adls1": (12.5, 6.5),
        "cosmos1": (16, 3.5), "dbw1": (16, 6.5), "tsi1": (19, 5),
        "operator1": (22, 5),
        "kv1": (5, 10), "log1": (9, 10), "mid1": (13, 10),
    },
    boundary_hints={
        "sub-prod": (2, 0.5, 22, 11),
        "rg-iot": (3, 1, 6, 7.5),
        "rg-analytics": (10, 1, 12, 7.5),
        "rg-shared": (3, 9, 12, 2.5),
    },
)


# ═════════════════════════════════════════════════════════════════
# REGISTRY: All reference architectures
# ═════════════════════════════════════════════════════════════════

REFERENCE_ARCHITECTURES: dict[str, ReferenceArchitecture] = {
    "baseline_foundry_chat": BASELINE_FOUNDRY_CHAT,
    "azure_landing_zone": AZURE_LANDING_ZONE,
    "baseline_web_app": BASELINE_WEB_APP,
    "ai_landing_zone": AI_LANDING_ZONE,
    "microservices_aks": MICROSERVICES_AKS,
    # ── New (grounded from Azure GitHub org review) ──
    "mission_critical_baseline": MISSION_CRITICAL_BASELINE,
    "container_apps_microservices": CONTAINER_APPS_MICROSERVICES,
    "iaas_baseline": IAAS_BASELINE,
    "app_service_ase": APP_SERVICE_ASE,
    "data_analytics_medallion": DATA_ANALYTICS_MEDALLION,
    "serverless_event_driven": SERVERLESS_EVENT_DRIVEN,
    "iot_reference": IOT_REFERENCE,
}


def get_reference_architecture(key: str) -> ReferenceArchitecture | None:
    """Look up a reference architecture by key."""
    return REFERENCE_ARCHITECTURES.get(key)


def list_reference_architectures() -> list[dict[str, str]]:
    """List all available reference architectures."""
    return [
        {
            "key": key,
            "name": arch.name,
            "category": arch.category,
            "description": arch.description,
            "source_url": arch.source_url,
        }
        for key, arch in REFERENCE_ARCHITECTURES.items()
    ]


def search_reference_architectures(query: str) -> list[dict[str, str]]:
    """Search reference architectures by name, category, or description."""
    q = query.lower()
    return [
        {
            "key": key,
            "name": arch.name,
            "category": arch.category,
            "description": arch.description,
            "source_url": arch.source_url,
        }
        for key, arch in REFERENCE_ARCHITECTURES.items()
        if q in arch.name.lower() or q in arch.category.lower() or q in arch.description.lower()
    ]
