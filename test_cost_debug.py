"""End-to-end test of pricing import from URL."""
import asyncio
import sys
sys.path.insert(0, "src")
from visio_mcp.pricing_import import fetch_estimate_from_url, generate_diagram_plan


async def main():
    result = await fetch_estimate_from_url("https://azure.com/e/d39891a84e674732b6794e47c6681ae7")
    print(f"URL: {result.url}")
    print(f"Error: {result.error}")
    print(f"Services: {len(result.services)}")
    print(f"Monthly: ${result.monthly_total:,.2f}")
    print(f"Annual:  ${result.annual_total:,.2f}")
    for s in result.services:
        print(f"  {s.name} -> {s.resource_type} (count={s.count})")

    if result.services:
        plan = generate_diagram_plan(result.services)
        print(f"\nDiagram: {plan['layout']}")
        print(f"  {len(plan['boundaries'])} boundaries, {len(plan['resources'])} resources, {len(plan['connections'])} connections")


asyncio.run(main())
