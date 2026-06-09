---
name: apply-reference-architecture
description: Apply one of the built-in Azure reference architecture templates to the current diagram.
argument-hint: name or description of the reference architecture (e.g. "AI Landing Zone")
agent: agent
tools: ['visio-azure/*']
---

# Apply an Azure reference architecture

Help me start from a vetted reference architecture instead of building from scratch.

Requested template: ${input:template:e.g. AI Landing Zone, Microservices on AKS, Baseline Web App}

Steps:

1. Call `list_reference_archs` to show the available templates and confirm which one
   best matches the request. If the request is vague, briefly recommend the closest
   match and proceed.
2. Optionally call `get_reference_arch_details` to summarize what the template
   includes before applying it.
3. Call `apply_reference_architecture` with the chosen template. Use merge mode if a
   diagram already exists; otherwise apply fresh.
4. Run `auto_layout` and then `validate_waf` and `validate_caf`, summarizing the
   results.
5. Report the final `get_diagram_state` summary and suggest sensible next
   customizations for the user's scenario.
