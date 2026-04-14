import * as vscode from "vscode";
import { McpServerManager } from "./mcpServer";
import { DiagramPreviewPanel } from "./diagramPreview";
import { ResourceTreeProvider } from "./views/resourceTree";
import { ConnectionTreeProvider } from "./views/connectionTree";
import { ValidationTreeProvider } from "./views/validationTree";

let mcpManager: McpServerManager;

export async function activate(context: vscode.ExtensionContext) {
  const outputChannel = vscode.window.createOutputChannel("Azure Visio");
  outputChannel.appendLine("Azure Visio AI Assistant activating...");

  // ── MCP Server Manager ─────────────────────────────────────────
  mcpManager = new McpServerManager(outputChannel);

  // ── Tree View Providers ────────────────────────────────────────
  const resourceTree = new ResourceTreeProvider(mcpManager);
  const connectionTree = new ConnectionTreeProvider(mcpManager);
  const validationTree = new ValidationTreeProvider(mcpManager);

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider("azureVisio.resources", resourceTree),
    vscode.window.registerTreeDataProvider(
      "azureVisio.connections",
      connectionTree
    ),
    vscode.window.registerTreeDataProvider(
      "azureVisio.validation",
      validationTree
    )
  );

  // ── Commands ───────────────────────────────────────────────────
  context.subscriptions.push(
    // Server lifecycle
    vscode.commands.registerCommand("azureVisio.startMcpServer", async () => {
      await mcpManager.start();
      vscode.window.showInformationMessage("Azure Visio MCP server started.");
    }),

    vscode.commands.registerCommand("azureVisio.stopMcpServer", async () => {
      await mcpManager.stop();
      vscode.window.showInformationMessage("Azure Visio MCP server stopped.");
    }),

    // Diagram operations
    vscode.commands.registerCommand("azureVisio.newDiagram", async () => {
      const name = await vscode.window.showInputBox({
        prompt: "Diagram name",
        value: "Azure Architecture",
      });
      if (!name) {
        return;
      }
      await mcpManager.callTool("new_diagram", { name });
      resourceTree.refresh();
      connectionTree.refresh();
      DiagramPreviewPanel.createOrShow(context.extensionUri, mcpManager);
    }),

    vscode.commands.registerCommand("azureVisio.openPreview", () => {
      DiagramPreviewPanel.createOrShow(context.extensionUri, mcpManager);
    }),

    vscode.commands.registerCommand("azureVisio.saveDiagram", async () => {
      const config = vscode.workspace.getConfiguration("azureVisio");
      const format = config.get<string>("defaultFormat", "drawio");

      const uri = await vscode.window.showSaveDialog({
        filters:
          format === "drawio"
            ? { "Draw.io Diagram": ["drawio"] }
            : { "Visio Diagram": ["vsdx"] },
        defaultUri: vscode.Uri.file(`diagram.${format}`),
      });
      if (!uri) {
        return;
      }

      const result = await mcpManager.callTool("save_diagram", {
        output_path: uri.fsPath,
        format,
      });
      vscode.window.showInformationMessage(
        `Diagram saved to ${uri.fsPath}`
      );
    }),

    // Add resource (quick pick from catalog)
    vscode.commands.registerCommand("azureVisio.addResource", async () => {
      const catalogResult = await mcpManager.callTool("list_shapes", {});
      if (!catalogResult?.shapes) {
        return;
      }

      const items = catalogResult.shapes.map(
        (s: { key: string; display_name: string; category: string }) => ({
          label: s.display_name,
          description: s.category,
          detail: s.key,
        })
      );

      const picked = await vscode.window.showQuickPick(items, {
        placeHolder: "Select an Azure resource type",
        matchOnDescription: true,
      });
      if (!picked) {
        return;
      }

      const displayName = await vscode.window.showInputBox({
        prompt: "Display name for this resource",
        value: picked.label,
      });
      if (!displayName) {
        return;
      }

      await mcpManager.callTool("add_resource", {
        resource_type: picked.detail,
        display_name: displayName,
      });

      resourceTree.refresh();
      DiagramPreviewPanel.update(mcpManager);
    }),

    // Add connection
    vscode.commands.registerCommand("azureVisio.addConnection", async () => {
      const state = await mcpManager.callTool("get_diagram_state", {});
      if (!state?.resources || Object.keys(state.resources).length < 2) {
        vscode.window.showWarningMessage(
          "Add at least 2 resources before creating a connection."
        );
        return;
      }

      const resourceItems = Object.values(state.resources).map(
        (r: any) => ({
          label: r.display_name,
          detail: r.id,
        })
      );

      const source = await vscode.window.showQuickPick(resourceItems, {
        placeHolder: "Select source resource",
      });
      if (!source) {
        return;
      }

      const target = await vscode.window.showQuickPick(
        resourceItems.filter((r: any) => r.detail !== source.detail),
        { placeHolder: "Select target resource" }
      );
      if (!target) {
        return;
      }

      await mcpManager.callTool("add_connection", {
        source_id: source.detail,
        target_id: target.detail,
      });

      connectionTree.refresh();
      DiagramPreviewPanel.update(mcpManager);
    }),

    // Add boundary
    vscode.commands.registerCommand("azureVisio.addBoundary", async () => {
      const types = [
        { label: "Resource Group", detail: "resource_group" },
        { label: "Virtual Network", detail: "virtual_network" },
        { label: "Subnet", detail: "subnet" },
        { label: "Subscription", detail: "subscription" },
        { label: "Region", detail: "region" },
        { label: "Availability Zone", detail: "availability_zone" },
      ];

      const picked = await vscode.window.showQuickPick(types, {
        placeHolder: "Select boundary type",
      });
      if (!picked) {
        return;
      }

      const name = await vscode.window.showInputBox({
        prompt: "Boundary display name",
        value: picked.label,
      });
      if (!name) {
        return;
      }

      await mcpManager.callTool("add_boundary", {
        boundary_type: picked.detail,
        display_name: name,
      });

      resourceTree.refresh();
      DiagramPreviewPanel.update(mcpManager);
    }),

    // Auto-layout
    vscode.commands.registerCommand("azureVisio.autoLayout", async () => {
      await mcpManager.callTool("auto_layout", {});
      DiagramPreviewPanel.update(mcpManager);
      vscode.window.showInformationMessage("Diagram auto-layout applied.");
    }),

    // WAF validation
    vscode.commands.registerCommand("azureVisio.validateWAF", async () => {
      const result = await mcpManager.callTool("validate_waf", {});
      validationTree.setReport("WAF", result);
      validationTree.refresh();
      vscode.window.showInformationMessage(
        `WAF Score: ${result?.score ?? "N/A"}/100`
      );
    }),

    // CAF validation
    vscode.commands.registerCommand("azureVisio.validateCAF", async () => {
      const result = await mcpManager.callTool("validate_caf", {});
      validationTree.setReport("CAF", result);
      validationTree.refresh();
      vscode.window.showInformationMessage(
        `CAF Score: ${result?.score ?? "N/A"}/100`
      );
    }),

    // Load reference architecture
    vscode.commands.registerCommand(
      "azureVisio.loadReferenceArch",
      async () => {
        const archList = await mcpManager.callTool(
          "list_reference_architectures",
          {}
        );
        if (!archList?.architectures) {
          return;
        }

        const items = archList.architectures.map(
          (a: { id: string; name: string; description: string }) => ({
            label: a.name,
            description: a.description,
            detail: a.id,
          })
        );

        const picked = await vscode.window.showQuickPick(items, {
          placeHolder: "Select a reference architecture",
          matchOnDescription: true,
        });
        if (!picked) {
          return;
        }

        await mcpManager.callTool("apply_reference_architecture", {
          architecture_id: picked.detail,
        });

        resourceTree.refresh();
        connectionTree.refresh();
        DiagramPreviewPanel.update(mcpManager);
        vscode.window.showInformationMessage(
          `Loaded: ${picked.label}`
        );
      }
    ),

    // Browse shape catalog
    vscode.commands.registerCommand(
      "azureVisio.browseShapeCatalog",
      async () => {
        const result = await mcpManager.callTool("list_shapes", {});
        if (!result?.shapes) {
          return;
        }

        const categories = [
          ...new Set(
            result.shapes.map((s: { category: string }) => s.category)
          ),
        ] as string[];

        const cat = await vscode.window.showQuickPick(categories, {
          placeHolder: "Filter by category (or press Escape to see all)",
        });

        const filtered = cat
          ? result.shapes.filter(
              (s: { category: string }) => s.category === cat
            )
          : result.shapes;

        const items = filtered.map(
          (s: { key: string; display_name: string; category: string }) => ({
            label: s.display_name,
            description: s.category,
            detail: s.key,
          })
        );

        const picked = await vscode.window.showQuickPick(items, {
          placeHolder: "Select a shape to add to the diagram",
          matchOnDescription: true,
        });

        if (picked) {
          await vscode.commands.executeCommand("azureVisio.addResource");
        }
      }
    )
  );

  // ── Auto-start server ──────────────────────────────────────────
  const config = vscode.workspace.getConfiguration("azureVisio");
  if (config.get<boolean>("autoStartServer", true)) {
    try {
      await mcpManager.start();
      outputChannel.appendLine("MCP server auto-started.");
    } catch (err) {
      outputChannel.appendLine(`MCP server auto-start failed: ${err}`);
    }
  }

  outputChannel.appendLine("Azure Visio AI Assistant activated.");
}

export function deactivate() {
  mcpManager?.stop();
}
