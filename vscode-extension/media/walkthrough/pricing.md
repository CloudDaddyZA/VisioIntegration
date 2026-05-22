# SKU & Pricing Guidance

Get live Azure pricing and tier recommendations for every resource in your diagram.

## What you can do

### Get SKU Recommendations
Ask for workload-based tier guidance:
```
@azureVisio /sku get recommendations for my diagram
```

### Query Live Pricing
Get real-time pricing from the Azure Retail Prices API:
```
@azureVisio /sku what does a P1v3 App Service cost in West Europe?
```

### Compare SKUs
Side-by-side comparison of different tiers:
```
@azureVisio /sku compare Standard vs Premium for Service Bus
```

## Data source

All pricing data comes from the **Azure Retail Prices API** — always up to date, no manual maintenance required.

## Tips

- Ask for pricing in a specific region for accurate estimates
- Compare SKUs before committing to a tier
- Use recommendations to right-size for your workload
