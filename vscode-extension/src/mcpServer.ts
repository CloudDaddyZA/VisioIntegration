import * as vscode from "vscode";
import * as cp from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as readline from "readline";

/**
 * Manages the lifecycle of the visio_mcp MCP server process and
 * provides a typed RPC interface for calling MCP tools.
 *
 * Communication uses JSON-RPC over stdin/stdout (MCP stdio transport).
 */
export class McpServerManager {
  private process: cp.ChildProcess | undefined;
  private outputChannel: vscode.OutputChannel;
  private extensionPath: string;
  private requestId = 0;
  private pendingRequests = new Map<
    number,
    {
      resolve: (value: any) => void;
      reject: (reason: any) => void;
    }
  >();
  private rl: readline.Interface | undefined;

  constructor(outputChannel: vscode.OutputChannel, extensionPath: string) {
    this.outputChannel = outputChannel;
    this.extensionPath = extensionPath;
  }

  // ── Lifecycle ──────────────────────────────────────────────────

  async start(): Promise<void> {
    if (this.process) {
      this.outputChannel.appendLine("MCP server already running.");
      return;
    }

    const pythonPath = this.resolvePythonPath();
    const workspaceRoot = this.resolveWorkspaceRoot();
    const srcPath = path.join(workspaceRoot, "src");

    this.outputChannel.appendLine(
      `Starting MCP server: ${pythonPath} -m visio_mcp.server`
    );
    this.outputChannel.appendLine(`  cwd: ${workspaceRoot}`);
    this.outputChannel.appendLine(`  PYTHONPATH: ${srcPath}`);
    this.outputChannel.show(true);

    this.process = cp.spawn(pythonPath, ["-m", "visio_mcp.server"], {
      cwd: workspaceRoot,
      env: {
        ...process.env,
        PYTHONPATH: srcPath,
      },
      stdio: ["pipe", "pipe", "pipe"],
    });

    // Stderr → output channel for logging
    this.process.stderr?.on("data", (data: Buffer) => {
      this.outputChannel.appendLine(`[MCP stderr] ${data.toString().trim()}`);
    });

    // Stdout → JSON-RPC line reader
    this.rl = readline.createInterface({
      input: this.process.stdout!,
      crlfDelay: Infinity,
    });

    this.rl.on("line", (line: string) => {
      this.handleServerLine(line);
    });

    this.process.on("exit", (code) => {
      this.outputChannel.appendLine(`MCP server exited (code ${code}).`);
      this.cleanup();
    });

    this.process.on("error", (err) => {
      this.outputChannel.appendLine(`MCP server error: ${err.message}`);
      this.cleanup();
    });

    // Send initialize
    await this.sendRequest("initialize", {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "azure-visio-vscode", version: "0.1.0" },
    });

    // Send initialized notification
    this.sendNotification("notifications/initialized", {});
  }

  async stop(): Promise<void> {
    if (!this.process) {
      return;
    }
    this.process.kill("SIGTERM");
    this.cleanup();
    this.outputChannel.appendLine("MCP server stopped.");
  }

  isRunning(): boolean {
    return this.process !== undefined;
  }

  // ── Tool calling ───────────────────────────────────────────────

  async callTool(
    toolName: string,
    args: Record<string, unknown>
  ): Promise<any> {
    if (!this.process) {
      await this.start();
    }

    const result = await this.sendRequest("tools/call", {
      name: toolName,
      arguments: args,
    });

    // MCP tool results come back as content array
    if (result?.content) {
      for (const item of result.content) {
        if (item.type === "text") {
          try {
            return JSON.parse(item.text);
          } catch {
            return item.text;
          }
        }
      }
    }
    return result;
  }

  async listTools(): Promise<any[]> {
    const result = await this.sendRequest("tools/list", {});
    return result?.tools ?? [];
  }

  // ── JSON-RPC transport ─────────────────────────────────────────

  private sendRequest(
    method: string,
    params: Record<string, unknown>
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.process?.stdin?.writable) {
        reject(new Error("MCP server not running"));
        return;
      }

      const id = ++this.requestId;
      this.pendingRequests.set(id, { resolve, reject });

      const message = JSON.stringify({
        jsonrpc: "2.0",
        id,
        method,
        params,
      });

      this.process.stdin.write(message + "\n");

      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Request ${method} timed out`));
        }
      }, 30_000);
    });
  }

  private sendNotification(
    method: string,
    params: Record<string, unknown>
  ): void {
    if (!this.process?.stdin?.writable) {
      return;
    }
    const message = JSON.stringify({
      jsonrpc: "2.0",
      method,
      params,
    });
    this.process.stdin.write(message + "\n");
  }

  private handleServerLine(line: string): void {
    const trimmed = line.trim();
    if (!trimmed) {
      return;
    }

    try {
      const msg = JSON.parse(trimmed);

      // Response to a request
      if (msg.id !== undefined && this.pendingRequests.has(msg.id)) {
        const { resolve, reject } = this.pendingRequests.get(msg.id)!;
        this.pendingRequests.delete(msg.id);

        if (msg.error) {
          reject(new Error(msg.error.message ?? JSON.stringify(msg.error)));
        } else {
          resolve(msg.result);
        }
        return;
      }

      // Server notification (log it)
      if (msg.method) {
        this.outputChannel.appendLine(
          `[MCP notification] ${msg.method}: ${JSON.stringify(msg.params)}`
        );
      }
    } catch {
      this.outputChannel.appendLine(`[MCP stdout] ${trimmed}`);
    }
  }

  // ── Path resolution ────────────────────────────────────────────

  private resolvePythonPath(): string {
    const config = vscode.workspace.getConfiguration("azureVisio");
    const custom = config.get<string>("pythonPath", "");
    if (custom) {
      return custom;
    }

    // Collect candidate roots: workspace folders + extension parent (project root)
    const roots: string[] = [];
    const folders = vscode.workspace.workspaceFolders;
    if (folders) {
      roots.push(...folders.map((f) => f.uri.fsPath));
    }
    // Extension lives in <projectRoot>/vscode-extension, so parent = project root
    const extensionParent = path.dirname(this.extensionPath);
    if (!roots.includes(extensionParent)) {
      roots.push(extensionParent);
    }

    this.outputChannel.appendLine(`Python search roots: ${roots.join(", ")}`);

    for (const root of roots) {
      const candidates = [
        path.join(root, ".venv", "Scripts", "python.exe"),
        path.join(root, ".venv", "bin", "python"),
      ];
      for (const venvPython of candidates) {
        this.outputChannel.appendLine(`Checking: ${venvPython}`);
        if (fs.existsSync(venvPython)) {
          this.outputChannel.appendLine(`Found Python: ${venvPython}`);
          return venvPython;
        }
      }
    }

    // Try python3 / python on PATH
    for (const name of ["python3", "python"]) {
      try {
        cp.execSync(`${name} --version`, { stdio: "ignore" });
        return name;
      } catch {
        // Try next
      }
    }

    throw new Error(
      "Python not found. Install Python or set azureVisio.pythonPath in settings."
    );
  }

  private resolveWorkspaceRoot(): string {
    const config = vscode.workspace.getConfiguration("azureVisio");
    const custom = config.get<string>("mcpServerPath", "");
    if (custom) {
      return custom;
    }

    const folders = vscode.workspace.workspaceFolders;
    if (folders) {
      return folders[0].uri.fsPath;
    }

    // Fallback: extension lives in <projectRoot>/vscode-extension
    const extensionParent = path.dirname(this.extensionPath);
    if (fs.existsSync(path.join(extensionParent, "src", "visio_mcp"))) {
      this.outputChannel.appendLine(
        `No workspace folder — using extension parent as project root: ${extensionParent}`
      );
      return extensionParent;
    }

    throw new Error(
      "No workspace folder open. Open the VisioIntegration folder first."
    );
  }

  private cleanup(): void {
    this.rl?.close();
    this.rl = undefined;
    this.process = undefined;

    // Reject all pending requests
    for (const [, { reject }] of this.pendingRequests) {
      reject(new Error("MCP server stopped"));
    }
    this.pendingRequests.clear();
  }
}
