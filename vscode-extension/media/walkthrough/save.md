# Save Your Diagram

Export your architecture to Visio (.vsdx) or Draw.io (.drawio) format.

## Supported formats

| Format | Requirements | Best for |
|--------|-------------|----------|
| `.drawio` | None (always available) | Sharing, editing in draw.io |
| `.vsdx` | Microsoft Visio installed | Enterprise documentation |

## How to save

**Option 1** — Command palette:
- Run **Azure Visio: Save Diagram**
- Choose a file location and format

**Option 2** — Chat:
```
@azureVisio /save
```
You'll be prompted to pick a save location.

## What's included in the export

- All resources with Azure icon stencils
- Connections with labels and line styles
- Boundary groups (resource groups, VNets, subnets)
- Auto-layout positioning
- Resource metadata and properties
