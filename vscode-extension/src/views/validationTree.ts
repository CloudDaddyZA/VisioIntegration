import * as vscode from "vscode";
import { McpServerManager } from "../mcpServer";

interface Finding {
  severity: string;
  pillar: string;
  message: string;
  recommendation: string;
}

interface ValidationReport {
  framework: string;
  score: number;
  findings: Finding[];
  summary: string;
}

/**
 * Tree data provider showing WAF/CAF validation results.
 */
export class ValidationTreeProvider
  implements vscode.TreeDataProvider<ValidationItem>
{
  private _onDidChangeTreeData = new vscode.EventEmitter<
    ValidationItem | undefined | void
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private reports: Map<string, ValidationReport> = new Map();

  constructor(private mcpManager: McpServerManager) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  setReport(framework: string, report: any): void {
    this.reports.set(framework, report as ValidationReport);
  }

  getTreeItem(element: ValidationItem): vscode.TreeItem {
    return element;
  }

  async getChildren(
    element?: ValidationItem
  ): Promise<ValidationItem[]> {
    if (!element) {
      // Top-level: show frameworks
      if (this.reports.size === 0) {
        return [
          new ValidationItem(
            "Run WAF or CAF validation to see results",
            "",
            vscode.TreeItemCollapsibleState.None,
            "info"
          ),
        ];
      }

      return [...this.reports.entries()].map(
        ([framework, report]) =>
          new ValidationItem(
            `${framework}: ${report.score}/100`,
            report.summary ?? "",
            vscode.TreeItemCollapsibleState.Expanded,
            report.score >= 80
              ? "pass"
              : report.score >= 50
                ? "warning"
                : "critical"
          )
      );
    }

    // Child level: show findings for a framework
    const framework = element.label?.toString().split(":")[0];
    if (!framework) {
      return [];
    }

    const report = this.reports.get(framework);
    if (!report?.findings) {
      return [];
    }

    return report.findings.map(
      (f) =>
        new ValidationItem(
          `[${f.severity}] ${f.message}`,
          f.recommendation,
          vscode.TreeItemCollapsibleState.None,
          f.severity === "critical"
            ? "critical"
            : f.severity === "warning"
              ? "warning"
              : "info"
        )
    );
  }
}

class ValidationItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly detail: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly severity: string
  ) {
    super(label, collapsibleState);
    this.description = detail;
    this.tooltip = `${label}\n${detail}`;

    switch (severity) {
      case "critical":
        this.iconPath = new vscode.ThemeIcon(
          "error",
          new vscode.ThemeColor("errorForeground")
        );
        break;
      case "warning":
        this.iconPath = new vscode.ThemeIcon(
          "warning",
          new vscode.ThemeColor("editorWarning.foreground")
        );
        break;
      case "pass":
        this.iconPath = new vscode.ThemeIcon(
          "pass",
          new vscode.ThemeColor("testing.iconPassed")
        );
        break;
      default:
        this.iconPath = new vscode.ThemeIcon("info");
    }

    this.contextValue = "validation-finding";
  }
}
