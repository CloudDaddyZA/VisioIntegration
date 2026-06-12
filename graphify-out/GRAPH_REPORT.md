# Graph Report - VisioIntegration  (2026-06-12)

## Corpus Check
- 84 files · ~176,832 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1116 nodes · 1856 edges · 76 communities (64 shown, 12 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 290 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `53712c69`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]

## God Nodes (most connected - your core abstractions)
1. `DiagramState` - 55 edges
2. `BoundaryGroup` - 43 edges
3. `Position` - 41 edges
4. `DiagramResource` - 39 edges
5. `Size` - 36 edges
6. `Connection` - 36 edges
7. `McpServerManager` - 26 edges
8. `CafValidator` - 25 edges
9. `LayoutEngine` - 25 edges
10. `WafValidator` - 24 edges

## Surprising Connections (you probably didn't know these)
- `DiagramResource` --uses--> `CafValidator`  [INFERRED]
  tests/test_caf_validator.py → src/visio_mcp/caf_validator.py
- `TestCafNaming` --uses--> `CafValidator`  [INFERRED]
  tests/test_caf_validator.py → src/visio_mcp/caf_validator.py
- `TestCafNamingPrefixes` --uses--> `CafValidator`  [INFERRED]
  tests/test_caf_validator.py → src/visio_mcp/caf_validator.py
- `TestCafResourceOrganization` --uses--> `CafValidator`  [INFERRED]
  tests/test_caf_validator.py → src/visio_mcp/caf_validator.py
- `TestCafScoring` --uses--> `CafValidator`  [INFERRED]
  tests/test_caf_validator.py → src/visio_mcp/caf_validator.py

## Import Cycles
- None detected.

## Communities (76 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (13): registerChatParticipant(), ToolCall, DiagramPreviewPanel, activate(), McpServerManager, ConnectionItem, ConnectionTreeProvider, ResourceItem (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (46): Any, Any, Any, main(), End-to-end test of pricing import from URL., Quick test for Azure SKU grounding module., test(), compare_azure_skus() (+38 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (42): Any, Any, check(), main(), Test: AI Landing Zone architecture creation via MCP tools.  Exercises the full, section(), Test reference architecture application and validation., test_all_reference_archs() (+34 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (37): 1. Clone and create virtual environment, 2. Install dependencies, 3. Download Azure icon stencils, 4. Configure AI provider, Adding a New Reference Architecture, Adding a New Resource Type, Architecture, Architecture Catalog (206 entries) (+29 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (34): activationEvents, categories, dependencies, @anthropic-ai/sdk, @modelcontextprotocol/sdk, description, devDependencies, esbuild (+26 more)

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (29): BoundaryGroup, Connection, DiagramResource, DiagramState, BoundaryGroup, Connection, DiagramResource, DiagramState (+21 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (16): Any, engine(), Unit tests for the Mermaid rendering engine., simple_diagram(), Save the current diagram as a Visio .vsdx, draw.io (.drawio), or Mermaid (.mmd), save_diagram(), _escape_label(), _humanize() (+8 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (16): DiagramState, layout(), Unit tests for the layout engine., LayoutEngine, Auto-layout engine for positioning Azure architecture diagram elements.  Layou, Ensure every resource is inside its assigned boundary.          For resources, Automatically positions resources, boundaries, and connections.      Uses Micr, Arrange resources in horizontal tiers from left to right.          If resource (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (30): default, description, type, default, description, type, default, description (+22 more)

### Community 9 - "Community 9"
Cohesion: 0.15
Nodes (16): DiagramState, ValidationFinding, caf(), CafValidator, Validates an architecture diagram against Azure CAF principles., Run all CAF principle checks and return a scored validation report.          E, Check CAF naming conventions: resource prefixes (e.g. vm-, aks-) and environment, Check resource organization: resource group boundaries, subscription hierarchy, (+8 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (17): _make_resource(), DiagramResource, Unit tests for the CAF validator engine., Tests for CAF scoring logic., Empty diagram should return a valid score., Properly named resources should score higher than poorly named ones., Tests for CAF naming convention validation., A VM named with full CAF pattern should pass all naming checks. (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.15
Nodes (15): Element, engine(), DrawioEngine, _hex_to_drawio(), _in2px(), Ensure a hex color has a '#' prefix for draw.io style strings., Renders a DiagramState into a .drawio (mxGraph XML) file., Return the absolute position (inches) of a parent boundary, or (0,0) for root. (+7 more)

### Community 12 - "Community 12"
Cohesion: 0.13
Nodes (18): BoundaryGroup, DiagramResource, Unit tests for the Draw.io rendering engine., Tests for specific rendering behaviors., Tests for the generated Draw.io XML structure., simple_diagram(), TestDrawioRendering, TestDrawioXmlStructure (+10 more)

### Community 13 - "Community 13"
Cohesion: 0.16
Nodes (15): DiagramState, ValidationFinding, waf(), Check Security pillar: Key Vault, managed identity, NSG/Firewall, private endpoi, Validates an architecture diagram against the Azure WAF pillars., Run all WAF pillar checks and return a scored validation report.          Eval, Check Cost Optimization pillar: autoscaling, premium SKU justification, standalo, Check Operational Excellence pillar: monitoring, CI/CD, Azure Policy. (+7 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (14): _create_openai_client(), Create the appropriate OpenAI client based on environment variables.      Supp, Any, Run the MCP session for the lifetime of the background loop., Call a tool on the MCP server (async, runs on the background loop)., Return tool definitions formatted for OpenAI function calling., Thread-safe wrapper around the Visio MCP server connection.      All MCP opera, Start the background event loop and connect to the MCP server (blocking). (+6 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (15): _make_resource(), Unit tests for the WAF validator engine., A well-architected diagram should score higher than a bare one., Tests for WAF Reliability pillar checks., Single compute resource should not trigger load balancer finding., Multiple compute resources without a load balancer should be critical., Multiple compute + load balancer should not trigger that finding., Tests for WAF Security pillar checks. (+7 more)

### Community 16 - "Community 16"
Cohesion: 0.17
Nodes (19): BaseModel, ValidationReport, ValidationReport, str, DiagramResource, Azure Cloud Adoption Framework (CAF) validator for architecture diagrams.  Ana, AzureServiceCategory, CafPrinciple (+11 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (22): Architecture, Architecture Knowledge, Boundary Types, Build & Run, CAF Naming, Copilot Instructions — Azure Visio MCP, Diagram CRUD, File Locations (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.10
Nodes (12): Connection, DiagramState, DiagramManager, Add a connection between two existing resources. Raises ValueError if either res, Remove a connection. Returns False if not found., Remove a boundary, unlink its child resources and sub-boundaries. Returns False, Assign a resource to a boundary group. Returns False if either is missing., Return all connections where the resource is source or target. (+4 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (12): Connections should produce edge cells., Boundaries should produce container cells., Diagram title should appear in the output., Empty diagram should produce valid XML with no resource cells., Resource display names should appear in the XML., Connection labels should appear in the XML., Helper to render and read back the XML., Engine should produce valid XML. (+4 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (20): 31 MCP Tools, 7 MCP Prompts, 8 MCP Resources, Azure Service Categories (19), Azure Visio MCP — Skill Definition, CAF Naming Prefixes, Capabilities, Key Domain Knowledge (+12 more)

### Community 21 - "Community 21"
Cohesion: 0.14
Nodes (12): DiagramState, Open .vssx stencil files if stencil_dir is provided., Embed the source image as a background trace on the page (COM)., Renders a DiagramState into a Visio .vsdx file., Draw a connector between two shapes using Microsoft Architecture Center conventi, Draw a numbered workflow step circle at the midpoint of a connector., Render the diagram state to a .vsdx file. Returns the output path., Add a title text block at the top of the page. (+4 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (20): `azure_catalog.py` (~1,490 lines), `azure_sku_grounding.py` (~340 lines), `caf_validator.py` (~383 lines), Capabilities, `diagram_state.py` (~209 lines), `drawio_engine.py` (~320 lines), `layout_engine.py` (~520 lines), `mermaid_engine.py` (~200 lines) (+12 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (19): _get_area(), _get_field(), _initials(), Any, SVG preview renderer for the diagram state in the browser., Render diagram state as HTML, with page tabs if the diagram has multiple pages., Get a field from a dict or pydantic model by trying multiple key names., Extract a numeric value from a dict or model attribute, with fallback default. (+11 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (16): Quick test of the architecture catalog integration., AzureArchitectureEntry, BoundaryTemplate, ConnectionTemplate, DiagramStandards, Azure Architecture Center reference architecture templates.  Based on official, A reference architecture or solution idea from Azure Architecture Center., A numbered workflow step shown on the diagram. (+8 more)

### Community 25 - "Community 25"
Cohesion: 0.13
Nodes (18): Any, Any, browse_architecture_catalog(), get_arch_catalog_entry(), Suggest cloud design patterns for a workload challenge or scenario.      Analy, Browse the Azure Architecture Catalog (206 architectures & solutions).      Fi, Search the Azure Architecture Catalog by keyword.      Searches across names,, Get full details for a specific Azure Architecture Catalog entry.      Use bro (+10 more)

### Community 26 - "Community 26"
Cohesion: 0.12
Nodes (15): compilerOptions, declaration, esModuleInterop, forceConsistentCasingInFileNames, lib, module, outDir, resolveJsonModule (+7 more)

### Community 27 - "Community 27"
Cohesion: 0.19
Nodes (14): _app_dir(), _ensure_std_streams(), _find_free_port(), main(), Path, Desktop launcher — runs Streamlit + pywebview as a native Windows app.  Starts, Entry point for the desktop app., Guarantee sys.stdout/sys.stderr are writable.      In a PyInstaller windowed b (+6 more)

### Community 28 - "Community 28"
Cohesion: 0.13
Nodes (12): MCP client that connects to the Visio Azure MCP server via stdio transport.  R, ensure_connection(), _get_gh_token(), init_session(), Interactive AI App for Azure Visio Diagram Creation ===========================, Run an async coroutine from synchronous Streamlit context., Initialize Streamlit session state keys for messages, MCP client, AI agent, and, Connect to MCP server if not already connected. Returns True on success, False o (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.17
Nodes (14): Any, apply_reference_architecture(), get_diagram_standards(), get_reference_arch_details(), list_reference_archs(), Reference architecture tools., Get detailed information about a reference architecture template.      Returns, Get Microsoft Azure Architecture Center diagram visual standards.      Returns (+6 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (14): ai_chat_architecture(), ai_landing_zone_architecture(), business_to_architecture(), getting_started(), hub_spoke_architecture(), microservices_architecture(), Prompt template for Azure Landing Zone hub-spoke architecture per Azure Architec, Prompt template for baseline zone-redundant web app per Azure Architecture Cente (+6 more)

### Community 31 - "Community 31"
Cohesion: 0.23
Nodes (11): _compact_tool_schemas(), _estimate_message_chars(), _prompt_save_location(), Any, AI agent that translates natural language into MCP tool calls using OpenAI., Open a native Save As dialog and return the chosen path (or None if cancelled)., Reduce token usage by stripping verbose descriptions from tool schemas., Estimate the character size of a message, excluding base64 image data. (+3 more)

### Community 32 - "Community 32"
Cohesion: 0.17
Nodes (8): AIAgent, _get_model(), Get the model name/deployment to use., Orchestrates natural-language interaction with the Visio MCP server., Build a key from env vars so we detect config changes., Reset the conversation history (keeps system prompt)., Inject a synthetic user/assistant exchange so the model knows about         sid, VisioMCPClient

### Community 33 - "Community 33"
Cohesion: 0.19
Nodes (10): AzureShapeInfo, get_shape(), Comprehensive catalog of Azure resource shapes and their Visio stencil mappings., Look up an Azure shape by key (resolves aliases)., Search shapes by name, category, or alias., Resolve a resource type alias to its canonical catalog key.      Handles commo, resolve_alias(), search_shapes() (+2 more)

### Community 34 - "Community 34"
Cohesion: 0.15
Nodes (12): Adding Tests, Running Tests, `test_ai_landing_zone.py`, `test_caf_validator.py`, `test_drawio_engine.py`, Test Files, `test_layout_engine.py`, `test_mermaid_engine.py` (+4 more)

### Community 35 - "Community 35"
Cohesion: 0.15
Nodes (7): _make_resource(), Resources without hints should still get valid positions., Grid layout should assign unique positions to all resources., Grid layout resources should not overlap., Tiered layout should separate networking, compute, and data resources., Auto-layout should modify and return the same state object., When layout hints are provided, resources should be placed at those exact positi

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (11): `ai_agent.py` (~400 lines), app/ — Interactive Streamlit AI Application, Architecture, `components/` — Custom Streamlit Components, Dependencies, `diagram_preview.py` (~350 lines), Environment Variables, `mcp_client.py` (~162 lines) (+3 more)

### Community 37 - "Community 37"
Cohesion: 0.23
Nodes (10): Path, _detect_icons_root(), get_icons_root(), Resolve the full filesystem path to an SVG icon for a resource type.      Reso, Locate the Azure Public Service Icons directory.      Tries the canonical bund, Return the default icons root directory (auto-detected)., resolve_svg_path(), Visio COM automation engine for rendering Azure architecture diagrams.  Uses w (+2 more)

### Community 38 - "Community 38"
Cohesion: 0.17
Nodes (11): architecture_catalog_resource(), boundary_styles_resource(), connector_styles_resource(), diagram_standards_resource(), Architecture catalog, styles, patterns, and resource tools., Full Azure Architecture Catalog — 206 reference architectures and solution ideas, Complete Azure shape catalog as a resource., Available connector/line styles. (+3 more)

### Community 39 - "Community 39"
Cohesion: 0.21
Nodes (7): _hex_to_rgb(), Draw a single resource shape using COM with named cells.          Strategy pri, Draw a resource with its original preserved visual style (COM)., Import an SVG file into the Visio page and position/size it.          Uses Pag, Draw a boundary/container rectangle per Microsoft Architecture Center standards., Convert '#RRGGBB' to 'R,G,B' string., Convert top-down layout Y to Visio bottom-up Y coordinate.

### Community 40 - "Community 40"
Cohesion: 0.17
Nodes (11): Building, Commands, Configuration, Copilot Chat Participant (`chatParticipant.ts`), Debugging, Extension Entry (`extension.ts`), Features, Key Implementation Details (+3 more)

### Community 41 - "Community 41"
Cohesion: 0.18
Nodes (10): Architecture & Dependency Map, Build & Run, Communication Protocols, Data Flow, Dependency Graph, Key Dependency Hubs, MCP Server (`src/visio_mcp/` — 23 files), Module Reference (+2 more)

### Community 42 - "Community 42"
Cohesion: 0.25
Nodes (10): extract_toc_entries(), get_repo_tree(), get_toc_data(), main(), parse_yml_frontmatter(), Fetch all browseable architecture YAML files from MicrosoftDocs/architecture-cen, Get the full file tree from GitHub., Get the TOC JSON for title/path mapping. (+2 more)

### Community 43 - "Community 43"
Cohesion: 0.20
Nodes (10): design_patterns_resource(), get_design_pattern_detail(), Azure Architecture Center cloud design patterns — CQRS, Event Sourcing, Saga, et, Get detailed information about a specific cloud design pattern.      Returns f, DesignPattern, get_design_pattern(), list_design_patterns(), An Azure Architecture Center cloud design pattern. (+2 more)

### Community 44 - "Community 44"
Cohesion: 0.28
Nodes (7): extract_all_from_tree(), find_all_nodes(), find_node(), main(), Extract all reference architectures from Azure Architecture Center TOC., Find ALL nodes matching the title (not just first)., Extract ALL architecture-like entries from entire category tree.

### Community 45 - "Community 45"
Cohesion: 0.31
Nodes (8): Any, import_image(), _import_svg_as_text(), import_vsdx(), Import tools — VSDX upload and image-to-diagram conversion., Import an existing Visio .vsdx file, parse its shapes into the current diagram,, Analyze an SVG file as structured XML text and convert to an Azure diagram., Import an image (screenshot, whiteboard photo, block diagram) and convert it

### Community 46 - "Community 46"
Cohesion: 0.25
Nodes (7): Authoring workflow, Azure diagram authoring, Conventions to enforce, Output formats, Prerequisite, Reference architectures, When to use

### Community 47 - "Community 47"
Cohesion: 0.29
Nodes (4): _add_icon_label(), _add_text_box(), Generate a 2-slide overview PowerPoint for the Visio Azure MCP project., Add an icon circle with label and description.

### Community 48 - "Community 48"
Cohesion: 0.25
Nodes (8): architecture_styles_resource(), Suggest the best-fit Azure architecture style for a workload description., Azure Architecture Center architecture styles — N-Tier, Microservices, Event-Dri, suggest_architecture_style(), list_architecture_styles(), List all available architecture styles., Suggest architecture styles based on a workload description.      Performs key, suggest_style_for_description()

### Community 49 - "Community 49"
Cohesion: 0.25
Nodes (7): Authoring workflow, Azure diagram authoring, Conventions to enforce, Output formats, Prerequisite, Reference architectures, When to use

### Community 50 - "Community 50"
Cohesion: 0.25
Nodes (7): Compare SKUs, Data source, Get SKU Recommendations, Query Live Pricing, SKU & Pricing Guidance, Tips, What you can do

### Community 51 - "Community 51"
Cohesion: 0.33
Nodes (4): Tests for the ValidationFinding model with Severity enum., String values should coerce to Severity enum members., Invalid severity string should raise validation error., TestWafFindingModel

### Community 52 - "Community 52"
Cohesion: 0.33
Nodes (6): get_architecture_style_detail(), Get detailed information about a specific architecture style.      Returns ful, ArchitectureStyle, get_architecture_style(), An Azure Architecture Center architecture style/pattern., Look up an architecture style by key.

### Community 53 - "Community 53"
Cohesion: 0.40
Nodes (4): Chat with @azureVisio, Example prompts, How it works, Slash commands

### Community 54 - "Community 54"
Cohesion: 0.40
Nodes (4): How to save, Save Your Diagram, Supported formats, What's included in the export

### Community 55 - "Community 55"
Cohesion: 0.40
Nodes (4): Cloud Adoption Framework (CAF), How to run, Validate with WAF & CAF, Well-Architected Framework (WAF)

### Community 56 - "Community 56"
Cohesion: 0.50
Nodes (3): paste_image_component(), Clipboard paste image component for Streamlit.  Uses a bidirectional Streamlit, Render a paste-target that captures clipboard images.      Returns:         B

### Community 57 - "Community 57"
Cohesion: 0.67
Nodes (3): build(), main(), Build the Azure Visio AI Assistant desktop app with PyInstaller.  Usage:

### Community 58 - "Community 58"
Cohesion: 0.50
Nodes (3): Tests for the CAF_NAMING_PREFIXES constant., Verify essential prefixes are defined., TestCafNamingPrefixes

### Community 59 - "Community 59"
Cohesion: 0.50
Nodes (4): Available Azure Architecture Center reference architecture templates., reference_architectures_resource(), list_reference_architectures(), List all available reference architectures.

### Community 60 - "Community 60"
Cohesion: 0.50
Nodes (3): How to use, Implement Improvements, What it can add

### Community 61 - "Community 61"
Cohesion: 0.50
Nodes (3): Available templates (16), How to use, Reference Architectures

## Knowledge Gaps
- **219 isolated node(s):** `name`, `displayName`, `description`, `version`, `publisher` (+214 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `enum` connect `Community 16` to `Community 8`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `azureVisio.defaultFormat` connect `Community 8` to `Community 16`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `DiagramState` (e.g. with `Element` and `DiagramState`) actually correct?**
  _`DiagramState` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `BoundaryGroup` (e.g. with `Element` and `BoundaryGroup`) actually correct?**
  _`BoundaryGroup` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `Position` (e.g. with `BoundaryGroup` and `Connection`) actually correct?**
  _`Position` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `DiagramResource` (e.g. with `Element` and `BoundaryGroup`) actually correct?**
  _`DiagramResource` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `Size` (e.g. with `BoundaryGroup` and `Connection`) actually correct?**
  _`Size` has 24 INFERRED edges - model-reasoned connections that need verification._