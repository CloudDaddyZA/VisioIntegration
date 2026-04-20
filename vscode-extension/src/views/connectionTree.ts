import * as vscode from "vscode";
import { McpServerManager } from "../mcpServer";

/**
 * Tree data provider showing connections in the current diagram.
 */
export class ConnectionTreeProvider
  implements vscode.TreeDataProvider<ConnectionItem>
{
  private _onDidChangeTreeData = new vscode.EventEmitter<
    ConnectionItem | undefined | void
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  constructor(private mcpManager: McpServerManager) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: ConnectionItem): vscode.TreeItem {
    return element;
  }

  async getChildren(): Promise<ConnectionItem[]> {
    if (!this.mcpManager.isRunning()) {
      return [];
    }

    try {
      const state = await this.mcpManager.callTool("get_diagram_state", {});
      if (!state?.connections) {
        return [];
      }

      const resources = state.resources ?? {};

      return Object.values(state.connections).map((c: any) => {
        const srcName =
          (resources[c.from ?? c.source_id] as any)?.name ??
          (resources[c.from ?? c.source_id] as any)?.display_name ??
          c.from ?? c.source_id;
        const tgtName =
          (resources[c.to ?? c.target_id] as any)?.name ??
          (resources[c.to ?? c.target_id] as any)?.display_name ??
          c.to ?? c.target_id;
        return new ConnectionItem(
          `${srcName} → ${tgtName}`,
          c.label ?? c.connection_type ?? "",
          c.id,
          vscode.TreeItemCollapsibleState.None
        );
      });
    } catch {
      return [];
    }
  }
}

class ConnectionItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly connectionLabel: string,
    public readonly connectionId: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState
  ) {
    super(label, collapsibleState);
    this.description = connectionLabel;
    this.tooltip = `${label}\n${connectionLabel}\nID: ${connectionId}`;
    this.iconPath = new vscode.ThemeIcon("arrow-right");
    this.contextValue = "connection";
  }
}
