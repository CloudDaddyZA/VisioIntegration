# Validate with WAF & CAF

Ensure your architecture follows Azure best practices before deploying.

## Well-Architected Framework (WAF)

Scores your diagram across **5 pillars**:

| Pillar | What it checks |
|--------|---------------|
| 🔒 Security | Private endpoints, firewalls, managed identity |
| 🛡️ Reliability | Multi-region, availability zones, redundancy |
| ⚡ Performance | Caching, CDN, autoscaling |
| 💰 Cost Optimization | Right-sizing, reserved capacity |
| 🔧 Operational Excellence | Monitoring, diagnostics, automation |

## Cloud Adoption Framework (CAF)

Validates naming conventions against Microsoft standards:
- `vm-` for Virtual Machines
- `app-` for App Services
- `vnet-` for Virtual Networks
- `kv-` for Key Vaults
- And 50+ more prefixes

## How to run

Use the command palette or ask in chat:
```
@azureVisio /validate
```
