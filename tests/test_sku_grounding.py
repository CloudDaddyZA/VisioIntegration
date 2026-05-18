"""Quick test for Azure SKU grounding module."""
import asyncio
import sys
sys.path.insert(0, "src")

from visio_mcp.azure_sku_grounding import (
    query_retail_prices,
    compare_sku_pricing,
    get_vm_family_recommendation,
    get_sku_reference_data,
)


async def test():
    # Test 1: Query VM pricing
    print("=== Test 1: Query VM pricing (eastus, D4s_v5) ===")
    results = await query_retail_prices(
        "Virtual Machines", region="eastus", sku_name="Standard_D4s_v5", max_results=5
    )
    for r in results[:3]:
        sku = r.get("skuName", "")
        meter = r.get("meterName", "")
        price = r.get("retailPrice", 0)
        region = r.get("region", "")
        print(f"  {sku} | {meter} | ${price}/hr | {region}")

    # Test 2: Compare SKUs
    print("\n=== Test 2: Compare VM SKUs ===")
    comparison = await compare_sku_pricing(
        "Virtual Machines",
        ["Standard_B2s", "Standard_D2s_v5", "Standard_D4s_v5"],
        region="eastus",
    )
    for c in comparison:
        print(f"  {c['skuName']} | ${c['hourlyPrice']}/hr | ~${c['monthlyEstimate']}/mo")

    # Test 3: Get recommendations
    print("\n=== Test 3: VM recommendation (general, production) ===")
    rec = get_vm_family_recommendation("general", "production")
    print(f"  Family: {rec['family']} - {rec['description']}")
    print(f"  Examples: {rec['examples']}")

    # Test 4: SKU reference for App Service
    print("\n=== Test 4: App Service reference data ===")
    ref = get_sku_reference_data("app_service")
    for tier, info in list(ref["tiers"].items())[:3]:
        print(f"  {tier}: {info['use_cases']} - {info['cost']}")

    print("\n=== All tests passed! ===")


if __name__ == "__main__":
    asyncio.run(test())
