# vscode-extension/ — VS Code Extension

A VS Code extension that integrates the Azure Visio MCP server directly into the editor,
providing commands, tree views, and a diagram preview panel.

---

## Features

- **13 Commands** — Create diagrams, add resources/connections/boundaries, auto-layout, validate WAF/CAF, load reference architectures, save, browse shape catalog, start/stop MCP server
- **3 Sidebar Tree Views** — Resources, Connections, and Validation findings in the Activity Bar
- **Diagram Preview** — Webview panel showing the current architecture diagram
- **Auto-start MCP Server** — Spawns the Python MCP server on activation, auto-detects `.venv` in the workspace or extension parent directory
- **JSON-RPC over stdio** — Communicates with the MCP server via stdin/stdout

---

## Commands

| Command | Description |
|---------|-------------|
| `Azure Visio: New Diagram` | Create a new blank diagram |
| `Azure Visio: Open Diagram Preview` | Open the diagram preview webview panel |
| `Azure Visio: Save Diagram` | Save the current diagram to `.vsdx` or `.drawio` |
| `Azure Visio: Add Resource` | Add an Azure resource to the diagram |
| `Azure Visio: Add Connection` | Connect two resources |
| `Azure Visio: Add Boundary Group` | Add a boundary (VNet, subnet, resource group, etc.) |
| `Azure Visio: Auto-Layout Diagram` | Apply automatic layout to the diagram |
| `Azure Visio: Validate WAF Alignment` | Run Well-Architected Framework validation |
| `Azure Visio: Validate CAF Naming` | Run Cloud Adoption Framework validation |
| `Azure Visio: Load Reference Architecture` | Apply one of 5 reference architecture templates |
| `Azure Visio: Browse Shape Catalog` | Browse the 123 Azure resource shape catalog |
| `Azure Visio: Start MCP Server` | Manually start the MCP server |
| `Azure Visio: Stop MCP Server` | Stop the running MCP server |

---

## Source Structure

```
vscode-extension/
├── package.json          # Extension manifest (commands, views, menus, config)
├── tsconfig.json         # TypeScript config
├── esbuild.js            # Build script (esbuild bundler)
├── src/
│   ├── extension.ts      # Entry point — command registration, tree view providers
│   ├── mcpServer.ts      # MCP server lifecycle (spawn, connect, reconnect, Python detection)
│   ├── diagramPreview.ts # Webview panel for diagram visualization
│   └── views/
│       ├── connectionTree.ts   # MCP connection status tree data provider
│       ├── resourceTree.ts     # Diagram resource list tree data provider
│       └── validationTree.ts   # WAF/CAF validation findings tree data provider
└── dist/
    └── extension.js      # Bundled output (esbuild)
```

---

## Key Implementation Details

### MCP Server Management (`mcpServer.ts`)

- **Python auto-detection**: Checks `.venv/Scripts/python.exe` in the workspace root, then falls back to `context.extensionPath` parent directory
- **Spawn**: Runs `python -m visio_mcp.server` with `PYTHONPATH=src` via stdio
- **Transport**: JSON-RPC over stdin/stdout using the MCP SDK
- **Reconnection**: Automatic restart on disconnect with configurable retry

### Extension Entry (`extension.ts`)

- **13 commands** registered via `vscode.commands.registerCommand`
- **Tool name mapping**: Maps VS Code commands to correct MCP tool names (`create_diagram`, `list_azure_shapes`, `add_azure_resource`, `connect_resources`, `list_reference_archs`)
- **Response field mapping**: Handles MCP response field names (`name` vs `display_name`, `from`/`to` vs `source_id`/`target_id`, etc.)
- **Tree views**: `ResourceTreeProvider`, `ConnectionTreeProvider`, `ValidationTreeProvider` with refresh on diagram changes

---

## Building

```powershell
cd vscode-extension
npm install
npm run compile    # esbuild bundle → dist/extension.js
```

## Debugging

Use the VS Code launch configuration `Run Extension` (in `.vscode/launch.json`) to start an Extension Development Host with the extension loaded.

---

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `azureVisio.pythonPath` | `""` (auto-detect) | Path to Python interpreter with `visio_mcp` installed |
| `azureVisio.mcpServerPath` | `""` (auto-detect) | Path to the `visio_mcp` source directory |

When left empty, the extension auto-detects the `.venv` Python in the workspace root or extension parent directory.
