"""Test reference architecture application and validation."""
import sys
sys.path.insert(0, r"d:\.github\VisioIntegration\src")

from visio_mcp.server import (
    apply_reference_architecture,
    validate_waf,
    validate_caf,
    get_diagram_state,
    list_reference_archs,
)

def test_all_reference_archs():
    archs = list_reference_archs()
    print(f"Available architectures: {archs['count']}")
    for a in archs["reference_architectures"]:
        print(f"  - {a['key']}: {a['name']}")
    print()

    for arch_info in archs["reference_architectures"]:
        key = arch_info["key"]
        print(f"{'='*60}")
        print(f"Testing: {arch_info['name']} ({key})")
        print(f"{'='*60}")

        result = apply_reference_architecture(key)
        print(f"  Status:      {result['status']}")
        print(f"  Resources:   {result['resource_count']}")
        print(f"  Connections: {result['connection_count']}")
        print(f"  Boundaries:  {result['boundary_count']}")
        print(f"  Workflow:    {len(result['workflow_steps'])} steps")

        waf = validate_waf()
        print(f"  WAF Score:   {waf['score']}/100 ({waf['finding_count']} findings)")

        caf = validate_caf()
        print(f"  CAF Score:   {caf['score']}/100 ({caf['finding_count']} findings)")

        state = get_diagram_state()
        print(f"  State:       {state['resource_count']} resources, "
              f"{state['connection_count']} connections, "
              f"{state['boundary_count']} boundaries")
        print()

if __name__ == "__main__":
    test_all_reference_archs()
    print("All reference architecture tests passed!")
