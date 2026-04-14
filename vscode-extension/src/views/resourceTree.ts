import * as vscode from "vscode";
import { McpServerManager } from "../mcpServer";

/**
 * Tree data provider showing resources in the current diagram.
 */
export class ResourceTreeProvider
  implements vscode.TreeDataProvider<ResourceItem>
{
  private _onDidChangeTreeData = new vscode.EventEmitter<
    ResourceItem | undefined | void
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  constructor(private mcpManager: McpServerManager) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: ResourceItem): vscode.TreeItem {
    return element;
  }

  async getChildren(): Promise<ResourceItem[]> {
    if (!this.mcpManager.isRunning()) {
      return [
        new ResourceItem(
          "MCP server not running",
          "",
          "",
          vscode.TreeItemCollapsibleState.None
        ),
      ];
    }

    try {
      const state = await this.mcpManager.callTool("get_diagram_state", {});
      if (!state?.resources) {
        return [];
      }

      return Object.values(state.resources).map(
        (r: any) =>
          new ResourceItem(
            r.display_name ?? r.id,
            r.resource_type ?? "unknown",
            r.id,
            vscode.TreeItemCollapsibleState.None
          )
      );
    } catch {
      return [];
    }
  }
}

class ResourceItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly resourceType: string,
    public readonly resourceId: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState
  ) {
    super(label, collapsibleState);
    this.description = resourceType;
    this.tooltip = `${label} (${resourceType})\nID: ${resourceId}`;
    this.iconPath = new vscode.ThemeIcon("symbol-field");
    this.contextValue = "resource";
  }
}
