import * as vscode from "vscode";
import { McpServerManager } from "./mcpServer";

/**
 * Webview panel that renders a live SVG preview of the current diagram.
 *
 * The preview is updated whenever the diagram state changes by
 * calling get_diagram_state and rendering a simple SVG visualization.
 */
export class DiagramPreviewPanel {
  public static currentPanel: DiagramPreviewPanel | undefined;
  private static readonly viewType = "azureVisio.diagramPreview";

  private readonly panel: vscode.WebviewPanel;
  private readonly extensionUri: vscode.Uri;
  private disposables: vscode.Disposable[] = [];

  private constructor(
    panel: vscode.WebviewPanel,
    extensionUri: vscode.Uri,
    mcpManager: McpServerManager
  ) {
    this.panel = panel;
    this.extensionUri = extensionUri;

    this.panel.onDidDispose(() => this.dispose(), null, this.disposables);

    // Initial content
    this.panel.webview.html = this.getLoadingHtml();
    this.updateContent(mcpManager);
  }

  static createOrShow(
    extensionUri: vscode.Uri,
    mcpManager: McpServerManager
  ): void {
    const column = vscode.ViewColumn.Beside;

    if (DiagramPreviewPanel.currentPanel) {
      DiagramPreviewPanel.currentPanel.panel.reveal(column);
      DiagramPreviewPanel.currentPanel.updateContent(mcpManager);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      DiagramPreviewPanel.viewType,
      "Azure Diagram Preview",
      column,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
      }
    );

    DiagramPreviewPanel.currentPanel = new DiagramPreviewPanel(
      panel,
      extensionUri,
      mcpManager
    );
  }

  static async update(mcpManager: McpServerManager): Promise<void> {
    if (DiagramPreviewPanel.currentPanel) {
      await DiagramPreviewPanel.currentPanel.updateContent(mcpManager);
    }
  }

  private async updateContent(mcpManager: McpServerManager): Promise<void> {
    try {
      const state = await mcpManager.callTool("get_diagram_state", {});
      this.panel.webview.html = this.getDiagramHtml(state);
    } catch (err) {
      this.panel.webview.html = this.getErrorHtml(
        err instanceof Error ? err.message : String(err)
      );
    }
  }

  private getDiagramHtml(state: any): string {
    const resources = state?.resources
      ? Object.values(state.resources)
      : [];
    const connections = state?.connections
      ? Object.values(state.connections)
      : [];
    const boundaries = state?.boundaries
      ? Object.values(state.boundaries)
      : [];
    const title = state?.name ?? "Azure Architecture";

    // Generate SVG content
    const PPI = 96;
    const pageW = (state?.page_width ?? 22) * PPI;
    const pageH = (state?.page_height ?? 17) * PPI;

    let svgContent = "";

    // Boundaries
    for (const b of boundaries as any[]) {
      const x = (b.position?.x ?? 0) * PPI;
      const y = (b.position?.y ?? 0) * PPI;
      const w = (b.size?.width ?? 3) * PPI;
      const h = (b.size?.height ?? 2) * PPI;
      svgContent += `
        <rect x="${x}" y="${y}" width="${w}" height="${h}"
              rx="8" ry="8"
              fill="rgba(0,120,212,0.05)" stroke="#0078D4"
              stroke-width="2" stroke-dasharray="8,4"/>
        <text x="${x + 10}" y="${y + 20}"
              font-size="13" font-weight="bold" fill="#0078D4">
          ${this.escapeHtml(b.display_name ?? b.id)}
        </text>`;
    }

    // Connections (simple lines)
    for (const c of connections as any[]) {
      const src = (resources as any[]).find(
        (r: any) => r.id === c.source_id
      );
      const tgt = (resources as any[]).find(
        (r: any) => r.id === c.target_id
      );
      if (src && tgt) {
        const sx = (src.position?.x ?? 0) * PPI + 30;
        const sy = (src.position?.y ?? 0) * PPI + 30;
        const tx = (tgt.position?.x ?? 0) * PPI + 30;
        const ty = (tgt.position?.y ?? 0) * PPI + 30;
        svgContent += `
          <line x1="${sx}" y1="${sy}" x2="${tx}" y2="${ty}"
                stroke="#0078D4" stroke-width="1.5"
                marker-end="url(#arrowhead)"/>`;
        if (c.label) {
          const mx = (sx + tx) / 2;
          const my = (sy + ty) / 2;
          svgContent += `
            <text x="${mx}" y="${my - 6}"
                  font-size="10" fill="#666" text-anchor="middle">
              ${this.escapeHtml(c.label)}
            </text>`;
        }
      }
    }

    // Resources
    for (const r of resources as any[]) {
      const x = (r.position?.x ?? 0) * PPI;
      const y = (r.position?.y ?? 0) * PPI;
      svgContent += `
        <rect x="${x}" y="${y}" width="60" height="60"
              rx="6" ry="6"
              fill="#fff" stroke="#0078D4" stroke-width="1.5"/>
        <text x="${x + 30}" y="${y + 35}"
              font-size="18" fill="#0078D4" text-anchor="middle">☁</text>
        <text x="${x + 30}" y="${y + 78}"
              font-size="10" fill="#333" text-anchor="middle">
          ${this.escapeHtml(r.display_name ?? r.id)}
        </text>`;
    }

    return /* html */ `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${this.escapeHtml(title)}</title>
  <style>
    body {
      margin: 0;
      padding: 16px;
      background: #1e1e1e;
      color: #d4d4d4;
      font-family: 'Segoe UI', sans-serif;
      overflow: auto;
    }
    h2 { color: #0078D4; margin: 0 0 12px; font-size: 16px; }
    .stats { font-size: 12px; color: #888; margin-bottom: 12px; }
    .canvas {
      background: #fff;
      border-radius: 8px;
      overflow: auto;
      padding: 8px;
    }
    svg { display: block; }
    .empty {
      text-align: center;
      padding: 60px 20px;
      color: #888;
    }
    .empty h3 { color: #0078D4; }
  </style>
</head>
<body>
  <h2>📐 ${this.escapeHtml(title)}</h2>
  <div class="stats">
    ${(resources as any[]).length} resources · 
    ${(connections as any[]).length} connections · 
    ${(boundaries as any[]).length} boundaries
  </div>
  ${
    (resources as any[]).length === 0
      ? `<div class="empty">
           <h3>No resources yet</h3>
           <p>Use the command palette or sidebar to add Azure resources.</p>
         </div>`
      : `<div class="canvas">
           <svg width="${pageW}" height="${pageH}"
                viewBox="0 0 ${pageW} ${pageH}"
                xmlns="http://www.w3.org/2000/svg">
             <defs>
               <marker id="arrowhead" markerWidth="10" markerHeight="7"
                       refX="10" refY="3.5" orient="auto">
                 <polygon points="0 0, 10 3.5, 0 7" fill="#0078D4"/>
               </marker>
             </defs>
             ${svgContent}
           </svg>
         </div>`
  }
</body>
</html>`;
  }

  private getLoadingHtml(): string {
    return /* html */ `<!DOCTYPE html>
<html><body style="display:flex;align-items:center;justify-content:center;
  height:100vh;background:#1e1e1e;color:#d4d4d4;font-family:'Segoe UI',sans-serif;">
  <p>Loading diagram preview…</p>
</body></html>`;
  }

  private getErrorHtml(message: string): string {
    return /* html */ `<!DOCTYPE html>
<html><body style="padding:20px;background:#1e1e1e;color:#d4d4d4;
  font-family:'Segoe UI',sans-serif;">
  <h3 style="color:#f44747;">Error loading diagram</h3>
  <p>${this.escapeHtml(message)}</p>
  <p style="color:#888;">Make sure the MCP server is running
    (command: <code>Azure Visio: Start MCP Server</code>).</p>
</body></html>`;
  }

  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  private dispose(): void {
    DiagramPreviewPanel.currentPanel = undefined;
    this.panel.dispose();
    for (const d of this.disposables) {
      d.dispose();
    }
    this.disposables = [];
  }
}
