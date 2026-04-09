"""Test: AI Landing Zone architecture creation via MCP tools.

Exercises the full MCP tool surface to build an enterprise AI Landing Zone
aligned with CAF and WAF, then validates the result.
"""

from __future__ import annotations

import json
import sys

sys.path.insert(0, "d:\\.github\\VisioIntegration\\src")

from visio_mcp.server import (
    add_azure_resource,
    add_boundary,
    assign_resource_to_boundary,
    auto_layout,
    connect_resources,
    create_diagram,
    get_diagram_state,
    get_waf_tips,
    list_azure_shapes,
    save_diagram,
    suggest_architecture_improvements,
    validate_caf,
    validate_waf,
)


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check(label: str, result: dict, expected_status: str = None) -> None:
    status = result.get("status", "ok")
    icon = "PASS" if (expected_status is None or status == expected_status) else "FAIL"
    print(f"  [{icon}] {label}: status={status}")
    if status == "error":
        print(f"         {result.get('message', '')}")
    return result


def main() -> None:
    print("AI LANDING ZONE - MCP Integration Test")
    print("=" * 60)

    # ── 1. Create diagram ─────────────────────────────────────────
    section("1. Create Diagram")
    r = check("create_diagram", create_diagram("AI Landing Zone - Enterprise"), "created")

    # ── 2. Verify shape catalog ───────────────────────────────────
    section("2. Shape Catalog Verification")
    ai_shapes = list_azure_shapes(category="AI + Machine Learning")
    print(f"  AI/ML shapes available: {ai_shapes['count']}")
    for s in ai_shapes["shapes"]:
        print(f"    - {s['key']}: {s['name']} (icon: {s['has_svg_icon']})")

    net_shapes = list_azure_shapes(search="firewall")
    print(f"  Firewall shapes found: {net_shapes['count']}")

    # ── 3. Build hierarchy: Management Group → Subscription → RGs ─
    section("3. CAF Resource Organization (Boundaries)")

    check("mgmt_group", add_boundary(
        "management_group", "mg-contoso-ai",
        boundary_id="mg-ai", x=0.5, y=0.5, width=21, height=16,
    ), "added")

    check("subscription", add_boundary(
        "subscription", "sub-ai-prod-001",
        boundary_id="sub-ai", x=1.0, y=1.5, width=20, height=14.5,
        parent_id="mg-ai",
    ), "added")

    # Resource groups
    rg_defs = [
        ("rg-network", "rg-ai-network-prod-eastus", 1.5, 2.5, 9, 6),
        ("rg-ai", "rg-ai-services-prod-eastus", 11, 2.5, 9, 6),
        ("rg-data", "rg-ai-data-prod-eastus", 1.5, 9.5, 9, 5.5),
        ("rg-shared", "rg-ai-shared-prod-eastus", 11, 9.5, 9, 5.5),
    ]
    for bid, name, x, y, w, h in rg_defs:
        check(f"boundary({bid})", add_boundary(
            "resource_group", name,
            boundary_id=bid, x=x, y=y, width=w, height=h,
            parent_id="sub-ai",
        ), "added")

    # VNet + Subnets inside networking RG
    check("vnet", add_boundary(
        "vnet", "vnet-ai-hub-prod-eastus",
        boundary_id="vnet-hub", x=2.0, y=3.0, width=8, height=5,
        parent_id="rg-network",
    ), "added")

    subnet_defs = [
        ("snet-gw", "snet-gateway", 2.5, 3.5, 3.5, 2),
        ("snet-ai", "snet-ai-services", 6.5, 3.5, 3, 2),
        ("snet-pe", "snet-private-endpoints", 2.5, 6.0, 7, 1.5),
    ]
    for sid, name, x, y, w, h in subnet_defs:
        check(f"subnet({sid})", add_boundary(
            "subnet", name,
            boundary_id=sid, x=x, y=y, width=w, height=h,
            parent_id="vnet-hub",
        ), "added")

    # ── 4. Add Resources ─────────────────────────────────────────
    section("4. Add Azure Resources")

    # -- Networking tier --
    network_resources = [
        ("firewall", "afw-ai-prod-001", "fw1", "snet-gw", 3.5, 4.2,
         '{"sku": "Premium", "threat_intel": "Alert"}'),
        ("application_gateway", "agw-ai-prod-001", "agw1", "snet-gw", 5.0, 4.2,
         '{"sku": "WAF_v2", "waf_mode": "Prevention"}'),
        ("bastion", "bas-ai-prod-001", "bastion1", "snet-gw", 3.5, 5.0, None),
        ("private_endpoint", "pep-openai-prod", "pe-oai", "snet-pe", 4.0, 6.5, None),
        ("private_endpoint", "pep-search-prod", "pe-search", "snet-pe", 6.0, 6.5, None),
        ("private_endpoint", "pep-storage-prod", "pe-stor", "snet-pe", 8.0, 6.5, None),
        ("nsg", "nsg-ai-services", "nsg1", "rg-network", 6.5, 5.2, None),
        ("dns_zone", "dnsz-privatelink", "dnsz1", "rg-network", 8.5, 5.2, None),
        ("ddos_protection", "ddos-ai-prod", "ddos1", "rg-network", 2.0, 7.5, None),
    ]

    for rtype, name, rid, gid, x, y, props in network_resources:
        check(f"resource({rid})", add_azure_resource(
            rtype, name, resource_id=rid, x=x, y=y,
            group_id=gid, properties=props,
        ), "added")

    # -- AI / ML tier --
    ai_resources = [
        ("openai_service", "oai-ai-prod-001", "oai1", "rg-ai", 12.5, 3.5,
         '{"model": "gpt-4o", "sku": "Standard"}'),
        ("ai_search", "srch-ai-prod-001", "search1", "rg-ai", 14.5, 3.5,
         '{"sku": "Standard", "replicas": 2}'),
        ("cognitive_services", "cog-ai-prod-001", "cog1", "rg-ai", 16.5, 3.5, None),
        ("machine_learning", "mlw-ai-prod-001", "mlw1", "rg-ai", 12.5, 5.5,
         '{"sku": "Enterprise"}'),
        ("bot_service", "bot-ai-prod-001", "bot1", "rg-ai", 14.5, 5.5, None),
        ("container_registry", "craciprod001", "cr1", "rg-ai", 16.5, 5.5, None),
        ("container_apps", "ca-ai-inference-prod", "ca1", "rg-ai", 18.0, 4.5,
         '{"min_replicas": 2, "scaling": "http"}'),
    ]

    for rtype, name, rid, gid, x, y, props in ai_resources:
        check(f"resource({rid})", add_azure_resource(
            rtype, name, resource_id=rid, x=x, y=y,
            group_id=gid, properties=props,
        ), "added")

    # -- Data tier --
    data_resources = [
        ("cosmos_db", "cosmos-ai-prod-001", "cosmos1", "rg-data", 3.0, 10.5,
         '{"api": "NoSQL", "multi_region_writes": true}'),
        ("storage_account", "staiprod001", "stor1", "rg-data", 5.0, 10.5,
         '{"replication": "GRS", "kind": "StorageV2"}'),
        ("data_lake_storage", "dlsaiprod001", "dls1", "rg-data", 7.0, 10.5,
         '{"replication": "GRS", "hierarchical_namespace": true}'),
        ("sql_database", "sqldb-ai-prod-001", "sql1", "rg-data", 3.0, 12.5,
         '{"sku": "BusinessCritical", "failover_group": true, "geo_replication": true}'),
        ("redis_cache", "redis-ai-prod-001", "redis1", "rg-data", 5.0, 12.5,
         '{"sku": "Premium", "zones": [1,2,3]}'),
        ("event_hub", "evh-ai-prod-001", "evh1", "rg-data", 7.0, 12.5,
         '{"sku": "Standard", "partitions": 8}'),
        ("service_bus", "sb-ai-prod-001", "sb1", "rg-data", 9.0, 11.5,
         '{"sku": "Premium"}'),
    ]

    for rtype, name, rid, gid, x, y, props in data_resources:
        check(f"resource({rid})", add_azure_resource(
            rtype, name, resource_id=rid, x=x, y=y,
            group_id=gid, properties=props,
        ), "added")

    # -- Shared services tier --
    shared_resources = [
        ("key_vault", "kv-ai-prod-001", "kv1", "rg-shared", 12.5, 10.5, None),
        ("managed_identity", "id-ai-prod-001", "mid1", "rg-shared", 14.5, 10.5, None),
        ("entra_id", "Contoso Entra ID", "entra1", "rg-shared", 16.5, 10.5, None),
        ("log_analytics", "log-ai-prod-001", "log1", "rg-shared", 12.5, 12.5, None),
        ("application_insights", "appi-ai-prod-001", "appi1", "rg-shared", 14.5, 12.5, None),
        ("monitor", "mon-ai-prod-001", "mon1", "rg-shared", 16.5, 12.5, None),
        ("defender_for_cloud", "Defender for Cloud", "defender1", "rg-shared", 18.0, 10.5, None),
        ("sentinel", "Microsoft Sentinel", "sentinel1", "rg-shared", 18.0, 12.5, None),
        ("policy", "Azure Policy", "policy1", "rg-shared", 12.5, 14.0, None),
        ("devops", "Azure DevOps", "devops1", "rg-shared", 14.5, 14.0, None),
    ]

    for rtype, name, rid, gid, x, y, props in shared_resources:
        check(f"resource({rid})", add_azure_resource(
            rtype, name, resource_id=rid, x=x, y=y,
            group_id=gid, properties=props,
        ), "added")

    # -- External actors --
    check("resource(user)", add_azure_resource(
        "user", "Data Scientists / Developers", resource_id="user1",
        x=0.5, y=4.0,
    ), "added")
    check("resource(internet)", add_azure_resource(
        "internet", "Internet / API Consumers", resource_id="inet1",
        x=0.5, y=6.0,
    ), "added")
    check("resource(on_prem)", add_azure_resource(
        "on_premises", "On-Premises Data Center", resource_id="onprem1",
        x=0.5, y=8.0,
    ), "added")

    # ── 5. Connect Resources ─────────────────────────────────────
    section("5. Connect Resources")

    connections = [
        # External → Gateway
        ("inet1", "agw1", "HTTPS", "data_flow"),
        ("user1", "bastion1", "RDP/SSH", "network"),
        ("onprem1", "fw1", "VPN/ER", "vpn_tunnel"),

        # Gateway → AI Services
        ("agw1", "ca1", "HTTPS", "data_flow"),
        ("fw1", "oai1", "HTTPS (filtered)", "data_flow"),
        ("ca1", "oai1", "OpenAI API", "data_flow"),
        ("ca1", "search1", "Search API", "data_flow"),
        ("ca1", "cog1", "AI Services", "data_flow"),

        # AI internal
        ("oai1", "search1", "RAG retrieval", "data_flow"),
        ("mlw1", "cr1", "Model images", "dependency"),
        ("mlw1", "oai1", "Fine-tuning", "data_flow"),
        ("bot1", "oai1", "Chat completions", "data_flow"),

        # AI → Data
        ("search1", "cosmos1", "Index source", "data_flow"),
        ("search1", "stor1", "Blob indexer", "data_flow"),
        ("oai1", "dls1", "Training data", "data_flow"),
        ("ca1", "sql1", "App data", "data_flow"),
        ("ca1", "redis1", "Cache", "data_flow"),
        ("ca1", "sb1", "Async tasks", "data_flow"),
        ("evh1", "cosmos1", "Event stream", "data_flow"),

        # Shared services dependencies
        ("oai1", "kv1", "API keys", "dependency"),
        ("ca1", "kv1", "Secrets", "dependency"),
        ("search1", "kv1", "Secrets", "dependency"),
        ("ca1", "mid1", "Auth", "dependency"),
        ("oai1", "mid1", "Auth", "dependency"),
        ("mid1", "entra1", "Token", "dependency"),

        # Monitoring
        ("ca1", "appi1", "Telemetry", "dependency"),
        ("oai1", "log1", "Diagnostics", "dependency"),
        ("search1", "log1", "Diagnostics", "dependency"),
        ("mon1", "log1", "Queries", "reference"),

        # Private endpoints
        ("pe-oai", "oai1", "Private Link", "network"),
        ("pe-search", "search1", "Private Link", "network"),
        ("pe-stor", "stor1", "Private Link", "network"),
    ]

    for src, tgt, label, ctype in connections:
        check(f"connect({src}→{tgt})", connect_resources(
            src, tgt, label=label, connection_type=ctype,
        ), "connected")

    # ── 6. Get WAF tips for key resources ─────────────────────────
    section("6. WAF Tips for Key AI Resources")
    for rtype in ["openai_service", "kubernetes_service", "cosmos_db", "key_vault"]:
        tips = get_waf_tips(rtype)
        name = tips.get("display_name", rtype)
        considerations = tips.get("waf_considerations", {})
        print(f"  {name}:")
        for pillar, tip in considerations.items():
            print(f"    [{pillar}] {tip[:80]}...")

    # ── 7. Auto-layout ────────────────────────────────────────────
    section("7. Auto-Layout")
    r = check("auto_layout(tiered)", auto_layout("tiered"), "layout_applied")
    print(f"  Positioned {len(r.get('positions', {}))} resources")

    # ── 8. Diagram State ──────────────────────────────────────────
    section("8. Diagram State Summary")
    state = get_diagram_state()
    print(f"  Name:        {state['name']}")
    print(f"  Resources:   {state['resource_count']}")
    print(f"  Connections: {state['connection_count']}")
    print(f"  Boundaries:  {state['boundary_count']}")

    # ── 9. WAF Validation ─────────────────────────────────────────
    section("9. WAF Validation")
    waf = validate_waf()
    print(f"  Score: {waf['score']}/100")
    print(f"  Summary: {waf['summary']}")
    print(f"  Findings ({waf['finding_count']}):")
    for f in waf["findings"]:
        sev = f["severity"].upper()
        print(f"    [{sev}] {f['pillar']}: {f['message']}")
        print(f"           → {f['recommendation'][:100]}")

    # ── 10. CAF Validation ────────────────────────────────────────
    section("10. CAF Validation")
    caf = validate_caf()
    print(f"  Score: {caf['score']}/100")
    print(f"  Summary: {caf['summary']}")
    print(f"  Findings ({caf['finding_count']}):")
    for f in caf["findings"]:
        sev = f["severity"].upper()
        print(f"    [{sev}] {f['principle']}: {f['message']}")
        print(f"           → {f['recommendation'][:100]}")

    # ── 11. Improvement Suggestions ───────────────────────────────
    section("11. Architecture Improvement Suggestions")
    suggestions = suggest_architecture_improvements()
    print(f"  WAF Score: {suggestions['waf_score']}/100")
    print(f"  CAF Score: {suggestions['caf_score']}/100")
    if suggestions["critical_issues"]:
        print(f"  Critical Issues ({len(suggestions['critical_issues'])}):")
        for issue in suggestions["critical_issues"]:
            print(f"    - [{issue['source']}] {issue['message']}")
    if suggestions["suggested_additions"]:
        print(f"  Suggested Additions ({len(suggestions['suggested_additions'])}):")
        for s in suggestions["suggested_additions"]:
            prio = s["priority"].upper()
            print(f"    [{prio}] Add {s['resource_type']}: {s['reason']}")
    else:
        print("  No additional resources suggested - architecture is comprehensive!")

    # ── 12. Save diagram ──────────────────────────────────────────
    section("12. Save Diagram")
    import os, signal, threading
    out_dir = "d:\\.github\\VisioIntegration\\output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ai-landing-zone.vsdx")

    # Save can hang if Visio COM shows a dialog; run with a timeout
    save_result = {"status": "timeout", "message": "Save timed out (Visio COM may not be available)"}
    save_done = threading.Event()

    def _do_save():
        nonlocal save_result
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass
        try:
            save_result = save_diagram(
                output_path=out_path,
                auto_layout_before_save=True,
                layout_strategy="tiered",
            )
        except Exception as exc:
            save_result = {"status": "error", "message": str(exc)}
        finally:
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except Exception:
                pass
            save_done.set()

    t = threading.Thread(target=_do_save, daemon=True)
    t.start()
    save_done.wait(timeout=20)  # 20 seconds max

    print(f"  Status:  {save_result.get('status')}")
    print(f"  Path:    {save_result.get('output_path', save_result.get('message'))}")
    print(f"  Method:  {save_result.get('rendering_method', 'N/A')}")

    # ── Summary ───────────────────────────────────────────────────
    section("TEST SUMMARY")
    print(f"  Diagram:     {state['name']}")
    print(f"  Resources:   {state['resource_count']}")
    print(f"  Connections: {state['connection_count']}")
    print(f"  Boundaries:  {state['boundary_count']}")
    print(f"  WAF Score:   {waf['score']}/100")
    print(f"  CAF Score:   {caf['score']}/100")
    print(f"  WAF Issues:  {waf['finding_count']}")
    print(f"  CAF Issues:  {caf['finding_count']}")

    # Pass/fail determination
    all_pass = (
        state["resource_count"] >= 30
        and state["connection_count"] >= 25
        and state["boundary_count"] >= 8
        and waf["score"] >= 40
        and caf["score"] >= 40
    )
    print(f"\n  {'ALL TESTS PASSED' if all_pass else 'SOME CHECKS NEED ATTENTION'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
