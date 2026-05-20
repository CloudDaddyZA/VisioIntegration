import * as vscode from "vscode";
import { McpServerManager } from "./mcpServer";
import { DiagramPreviewPanel } from "./diagramPreview";

/**
 * GitHub Copilot Chat participant for Azure architecture diagrams.
 *
 * Usage in Copilot Chat:
 *   @azureVisio draw a 3-tier web app
 *   @azureVisio validate WAF
 *   @azureVisio recommend SKUs for production
 *   @azureVisio save diagram as visio
 */

const PARTICIPANT_ID = "azure-visio-assistant.azureVisio";

const SYSTEM_PROMPT = `You are an Azure architecture diagram assistant integrated into VS Code via GitHub Copilot Chat.
You help users create, modify, and validate Azure architecture diagrams using MCP tools.

You can:
- Create diagrams and add Azure resources (VMs, App Services, databases, etc.)
- Add boundaries (VNets, subnets, resource groups)
- Connect resources with labeled arrows
- Apply reference architectures from Microsoft Architecture Center (16 templates)
- Auto-layout diagrams (tiered, grouped, hybrid strategies)
- Validate against WAF (Well-Architected Framework) and CAF (Cloud Adoption Framework)
- Recommend SKUs with live Azure pricing data
- Save diagrams as .vsdx (Visio) or .drawio files

CRITICAL PARAMETER RULES:
- The "properties" parameter is OPTIONAL. Only pass it if you need metadata. When you DO pass it, it must be a JSON STRING like: "properties": "{\\"sku\\": \\"Standard_D4s_v5\\"}" — NOT an object.
- Omit "properties" entirely if you have nothing to add. This avoids formatting errors.
- The "parent_boundary_id" parameter is optional. Omit it to place a boundary at the top level.
- Use simple string values for all parameters unless the schema explicitly says otherwise.

Guidelines:
1. When the user describes an architecture, break it into steps: create diagram → add boundaries → add resources → connect them → auto-layout → validate.
2. Use descriptive CAF-aligned names (e.g., 'rg-app-prod-eastus', 'vm-web-prod-001').
3. Always suggest running WAF and CAF validation after building a diagram.
4. For common patterns, suggest using reference architectures first.
5. Explain what you're doing at each step.
6. When multiple resources need to be added, add them one by one.
7. After adding resources and connections, apply auto_layout for clean arrangement.
8. When saving, suggest a descriptive filename. Use just the filename — the server resolves to output/ automatically.
9. For business requirements, use suggest_architecture_style and search_arch_catalog to find best-fit patterns.
10. Proactively suggest missing resources (WAF, Key Vault, monitoring) and redundancy improvements.
11. Use get_sku_recommendations, query_azure_pricing, and compare_azure_skus for sizing guidance.
12. After validation, summarize scores and top recommendations.

IMPORTANT: You must call the tools to perform actions. Do NOT just describe what you would do — actually call the tools.`;

interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

/**
 * Parse the AI model's response to extract tool calls.
 * The model is instructed to emit tool calls in a structured format.
 */
function parseToolCalls(text: string): ToolCall[] {
  const calls: ToolCall[] = [];
  // Match ```tool\n{...}\n``` blocks
  const toolBlockRegex = /```tool\s*\n([\s\S]*?)\n```/g;
  let match: RegExpExecArray | null;
  while ((match = toolBlockRegex.exec(text)) !== null) {
    try {
      const parsed = JSON.parse(match[1]);
      if (parsed.name && parsed.arguments !== undefined) {
        calls.push({ name: parsed.name, arguments: parsed.arguments });
      }
    } catch {
      // Skip malformed blocks
    }
  }
  return calls;
}

export function registerChatParticipant(
  context: vscode.ExtensionContext,
  mcpManager: McpServerManager
): void {
  const handler: vscode.ChatRequestHandler = async (
    request: vscode.ChatRequest,
    chatContext: vscode.ChatContext,
    stream: vscode.ChatResponseStream,
    token: vscode.CancellationToken
  ): Promise<vscode.ChatResult> => {
    // Ensure MCP server is running
    if (!mcpManager.isRunning()) {
      stream.progress("Starting MCP server...");
      try {
        await mcpManager.start();
      } catch (err) {
        stream.markdown(
          `**Error**: Could not start the MCP server. Ensure Python and visio_mcp are installed.\n\n\`${err}\``
        );
        return {};
      }
    }

    // Get available tools from MCP
    let tools: any[];
    try {
      tools = await mcpManager.listTools();
    } catch {
      tools = [];
    }

    // Build tool descriptions for the model
    const toolDescriptions = tools
      .map((t: any) => {
        const params = t.inputSchema?.properties ?? {};
        const required = new Set(t.inputSchema?.required ?? []);
        const paramList = Object.entries(params)
          .map(([k, v]: [string, any]) => {
            const req = required.has(k) ? "required" : "optional";
            return `    ${k} (${v.type ?? "string"}, ${req}): ${v.description ?? ""}`;
          })
          .join("\n");
        return `- **${t.name}**: ${t.description ?? ""}\n  Parameters:\n${paramList}`;
      })
      .join("\n\n");

    // Build conversation history from chat context
    const history: Array<{ role: string; content: string }> = [];
    for (const turn of chatContext.history) {
      if (turn instanceof vscode.ChatRequestTurn) {
        history.push({ role: "user", content: turn.prompt });
      } else if (turn instanceof vscode.ChatResponseTurn) {
        const parts: string[] = [];
        for (const part of turn.response) {
          if (part instanceof vscode.ChatResponseMarkdownPart) {
            parts.push(part.value.value);
          }
        }
        if (parts.length > 0) {
          history.push({ role: "assistant", content: parts.join("\n") });
        }
      }
    }

    // Use VS Code Language Model API (Copilot model)
    const messages: vscode.LanguageModelChatMessage[] = [
      vscode.LanguageModelChatMessage.User(
        `${SYSTEM_PROMPT}\n\nAvailable MCP tools:\n${toolDescriptions}\n\nTo call a tool, emit a fenced block like:\n\`\`\`tool\n{"name": "tool_name", "arguments": {"param": "value"}}\n\`\`\`\n\nYou can call multiple tools in sequence. After tool results come back, continue your response.`
      ),
    ];

    // Add conversation history
    for (const msg of history) {
      if (msg.role === "user") {
        messages.push(vscode.LanguageModelChatMessage.User(msg.content));
      } else {
        messages.push(vscode.LanguageModelChatMessage.Assistant(msg.content));
      }
    }

    // Add current user request
    messages.push(vscode.LanguageModelChatMessage.User(request.prompt));

    // Select a model (prefer GPT-4o family)
    const models = await vscode.lm.selectChatModels({
      vendor: "copilot",
      family: "gpt-4o",
    });

    if (models.length === 0) {
      stream.markdown(
        "**Error**: No language model available. Ensure GitHub Copilot Chat is active."
      );
      return {};
    }

    const model = models[0];

    // Agentic loop: send to model, execute tools, feed results back
    const maxIterations = 10;
    for (let iteration = 0; iteration < maxIterations; iteration++) {
      if (token.isCancellationRequested) {
        break;
      }

      stream.progress(
        iteration === 0 ? "Thinking..." : "Executing tools..."
      );

      let fullResponse = "";
      try {
        const response = await model.sendRequest(messages, {}, token);
        for await (const chunk of response.text) {
          fullResponse += chunk;
        }
      } catch (err) {
        if (err instanceof vscode.LanguageModelError) {
          stream.markdown(`**Model error**: ${err.message}`);
        } else {
          stream.markdown(`**Error**: ${err}`);
        }
        return {};
      }

      // Check for tool calls in the response
      const toolCalls = parseToolCalls(fullResponse);

      if (toolCalls.length === 0) {
        // No more tool calls — stream the final response
        stream.markdown(fullResponse);
        break;
      }

      // Execute tool calls and collect results
      const resultParts: string[] = [];
      for (const call of toolCalls) {
        stream.progress(`Calling ${call.name}...`);
        // Auto-fix: if "properties" is an object, stringify it
        if (
          call.arguments.properties &&
          typeof call.arguments.properties === "object"
        ) {
          call.arguments.properties = JSON.stringify(call.arguments.properties);
        }
        try {
          const result = await mcpManager.callTool(call.name, call.arguments);
          const resultStr =
            typeof result === "string" ? result : JSON.stringify(result, null, 2);
          resultParts.push(
            `Tool \`${call.name}\` result:\n\`\`\`json\n${resultStr}\n\`\`\``
          );
        } catch (err) {
          resultParts.push(
            `Tool \`${call.name}\` error: ${err instanceof Error ? err.message : String(err)}`
          );
        }
      }

      // Show the non-tool parts of the response to the user
      const textBeforeTools = fullResponse
        .replace(/```tool\s*\n[\s\S]*?\n```/g, "")
        .trim();
      if (textBeforeTools) {
        stream.markdown(textBeforeTools + "\n\n");
      }

      // Add assistant message and tool results to conversation
      messages.push(
        vscode.LanguageModelChatMessage.Assistant(fullResponse)
      );
      messages.push(
        vscode.LanguageModelChatMessage.User(
          `Tool execution results:\n\n${resultParts.join("\n\n")}\n\nContinue based on these results. If the task is complete, provide a summary. If more tools need to be called, call them.`
        )
      );
    }

    // Update the diagram preview if it's open
    DiagramPreviewPanel.update(mcpManager);

    return {};
  };

  // Register the chat participant
  const participant = vscode.chat.createChatParticipant(
    PARTICIPANT_ID,
    handler
  );
  participant.iconPath = vscode.Uri.joinPath(
    context.extensionUri,
    "media",
    "icon.png"
  );

  context.subscriptions.push(participant);
}
