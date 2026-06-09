---
name: validate-and-improve
description: Validate the current Azure diagram against WAF and CAF, then apply the recommended improvements.
argument-hint: optional focus area (e.g. "security", "cost", "naming")
agent: agent
tools: ['visio-azure/*']
---

# Validate and improve the current diagram

Review the current Azure architecture diagram and raise its quality.

Optional focus: ${input:focus:leave blank for a full review, or specify e.g. security / cost / reliability / naming}

Steps:

1. Call `get_diagram_state` to load the current diagram. If it is empty, tell the
   user there is nothing to validate and stop.
2. Call `validate_waf` and `validate_caf`. Summarize the scores and the most
   impactful findings (highlight the requested focus area if one was given).
3. Call `suggest_architecture_improvements` for AI-driven recommendations.
4. Propose a short, prioritized list of concrete changes (add resources, fix CAF
   naming, add boundaries, add missing connections). Ask for confirmation before
   modifying the diagram.
5. After confirmation, apply the agreed changes with the relevant tools, run
   `auto_layout`, and re-run `validate_waf` / `validate_caf` to show the improvement.

Do not save the diagram unless the user explicitly asks.
