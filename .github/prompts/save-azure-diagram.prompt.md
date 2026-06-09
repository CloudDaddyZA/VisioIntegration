---
name: save-azure-diagram
description: Save the current Azure diagram to a Visio (.vsdx), draw.io (.drawio), or Mermaid (.mmd) file.
argument-hint: format — vsdx | drawio | mmd (and optional output path)
agent: agent
tools: ['visio-azure/*']
---

# Save the current diagram

Render and save the current Azure architecture diagram.

Requested format: ${input:format:vsdx, drawio, or mmd}

Steps:

1. Call `get_diagram_state` to confirm there is a diagram to save. If it is empty,
   tell the user and stop.
2. Determine the output format:
   - `.vsdx` — Microsoft Visio (requires Visio/COM, falls back to python-vsdx)
   - `.drawio` — draw.io / diagrams.net (always available)
   - `.mmd` — Mermaid flowchart text (always available, dependency-free)
3. Call `save_diagram` with the chosen format and an output path. If the user did
   not provide a path, pick a sensible filename in the workspace `output/` folder and
   tell them where it was written.
4. Confirm success and report the absolute path of the saved file.
