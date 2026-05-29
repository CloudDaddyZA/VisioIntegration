# Azure Visio AI — Instruction Video Script & Storyboard

A ready-to-record narration with shot-by-shot on-screen actions for both the
**Streamlit web app** and the **VS Code extension** (`@azureVisio`).

- **Target length:** ~3 minutes (2 segments: ~1:45 app + ~1:15 extension)
- **Recommended tools:** [OBS Studio](https://obsproject.com) or Windows Clipchamp for capture; 1080p/30fps.
- **Tip:** A self-playing visual companion lives at [walkthrough.html](walkthrough.html) — open it in a browser and screen-record it if you don't want to record the live UI.

---

## Segment 1 — Streamlit Web App (~1:45)

### Shot 1 · Title (0:00–0:08)
- **On screen:** App open at `http://localhost:8501`, sidebar visible.
- **Narration:** "Meet Azure Visio AI — a conversational assistant that turns plain English into production-quality Azure architecture diagrams, with official icons and Well-Architected validation built in."

### Shot 2 · Connect & configure (0:08–0:25)
- **On screen:** Point to the sidebar "Connected · N tools" badge, then expand **AI Configuration**, showing the GitHub Copilot / OpenAI / Azure OpenAI options.
- **Action:** Hover the green "Connected" badge.
- **Narration:** "On launch it auto-connects to the MCP server and detects your GitHub Copilot login. You can also plug in OpenAI or Azure OpenAI keys under AI Configuration."

### Shot 3 · Describe an architecture (0:25–0:50)
- **On screen:** Click the chat box at the bottom.
- **Action:** Type: `Build me a 3-tier web app with App Service, SQL Database, and a Key Vault, all inside a VNet.` Press Enter.
- **Narration:** "Just describe what you need. The assistant picks Azure services, applies Cloud Adoption Framework naming, lays everything out, and draws boundaries automatically."

### Shot 4 · Live diagram preview (0:50–1:05)
- **On screen:** The center "Diagram Preview" pane renders the diagram with Azure icons; sidebar "Current Diagram" shows resource/connection/boundary counts.
- **Narration:** "The diagram appears live — with real Azure icons, a virtual-network boundary, and labeled connectors."

### Shot 5 · Business → Architecture & templates (1:05–1:20)
- **On screen:** Sidebar — show the **Business → Architecture** textarea and the **Reference Architectures** dropdown.
- **Action:** Open the template dropdown to reveal "AI Landing Zone", "Microservices on AKS", etc.
- **Narration:** "Prefer a head start? Describe a business goal to auto-design it, or apply one of the built-in reference architectures."

### Shot 6 · Validate WAF (1:20–1:32)
- **On screen:** Click **Validate WAF** under Quick Actions; the chat shows a score and findings.
- **Narration:** "One click validates the design against the five Well-Architected pillars and flags improvements."

### Shot 7 · Save with format choice (1:32–1:45)
- **On screen:** Sidebar **Save Diagram** — show the format radio (Visio .vsdx / draw.io .drawio / Mermaid .mmd), then click Save and let the native Save-As dialog appear.
- **Narration:** "Export to Visio, draw.io, or Mermaid — a native save dialog lets you choose exactly where it lands."

---

## Segment 2 — VS Code Extension (~1:15)

### Shot 8 · Open Copilot Chat (1:45–1:58)
- **On screen:** VS Code with the Copilot Chat panel open.
- **Action:** Type `@azureVisio` to show the participant in the picker.
- **Narration:** "The same engine lives right inside VS Code. Open Copilot Chat and call the at-azureVisio participant."

### Shot 9 · Generate from chat (1:58–2:20)
- **On screen:** Send: `@azureVisio create a hub-and-spoke network with a firewall and two spoke VNets`.
- **Action:** Let the response stream and tool calls run.
- **Narration:** "Describe the architecture in chat — it builds the diagram step by step using the MCP tools, no context-switching required."

### Shot 10 · Preview panel (2:20–2:35)
- **On screen:** Run **Azure Visio: Open Preview** from the Command Palette (`Ctrl+Shift+P`); the diagram preview webview opens beside the editor.
- **Narration:** "Open the live preview panel to see the rendered diagram update as you iterate."

### Shot 11 · Commands & settings (2:35–2:55)
- **On screen:** Command Palette filtered to "Azure Visio" showing Save Diagram, Add Resource, Validate, etc. Then Settings → `azureVisio.defaultFormat` (vsdx / drawio / mermaid).
- **Narration:** "Fourteen commands cover everything — add resources, validate, load templates, and save. Set your default output format in settings."

### Shot 12 · Save & wrap (2:55–3:05)
- **On screen:** Run **Azure Visio: Save Diagram**; native save dialog appears with the format filter.
- **Narration:** "Save to Visio, draw.io, or Mermaid — and you're done. From idea to a polished Azure diagram in minutes. That's Azure Visio AI."

---

## Quick capture checklist
- [ ] Start the app: `streamlit run app/streamlit_app.py`
- [ ] Pre-clear the chat so the demo starts fresh
- [ ] Hide secrets/tokens before recording (collapse AI Configuration)
- [ ] Set display scaling to 100% for crisp icons
- [ ] Record audio narration separately for cleaner edits
