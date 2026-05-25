"""Unit tests for the CAF validator engine."""

import pytest

from visio_mcp.models import (
    BoundaryGroup,
    DiagramResource,
    DiagramState,
    Position,
    Severity,
    Size,
    CafPrinciple,
)
from visio_mcp.caf_validator import CafValidator, CAF_NAMING_PREFIXES


@pytest.fixture
def caf():
    return CafValidator()


@pytest.fixture
def empty_diagram():
    return DiagramState(name="Test Diagram")


def _make_resource(resource_type: str, name: str, group_id: str | None = None) -> DiagramResource:
    return DiagramResource(
        id=name,
        resource_type=resource_type,
        display_name=name,
        group_id=group_id,
    )


class TestCafNaming:
    """Tests for CAF naming convention validation."""

    def test_correctly_named_vm(self, caf, empty_diagram):
        """A VM named with full CAF pattern should pass all naming checks."""
        empty_diagram.resources["vm-web-prod-eastus-01"] = _make_resource("virtual_machine", "vm-web-prod-eastus-01")
        report = caf.validate(empty_diagram)
        naming_findings = [
            f for f in report.findings
            if f.pillar == CafPrinciple.NAMING and "vm-web-prod-eastus-01" in f.affected_resources
        ]
        assert len(naming_findings) == 0

    def test_incorrectly_named_vm(self, caf, empty_diagram):
        """A VM named 'MyServer' should fail naming checks."""
        empty_diagram.resources["MyServer"] = _make_resource("virtual_machine", "MyServer")
        report = caf.validate(empty_diagram)
        naming_findings = [
            f for f in report.findings
            if f.pillar == CafPrinciple.NAMING and "MyServer" in f.affected_resources
        ]
        assert len(naming_findings) >= 1

    def test_correctly_named_vnet(self, caf, empty_diagram):
        """A VNet named 'vnet-hub-001' should pass."""
        empty_diagram.boundaries["vnet-hub-001"] = BoundaryGroup(
            id="vnet-hub-001",
            boundary_type="virtual_network",
            display_name="vnet-hub-001",
        )
        report = caf.validate(empty_diagram)
        vnet_findings = [
            f for f in report.findings
            if f.pillar == CafPrinciple.NAMING and "vnet-hub-001" in f.affected_resources
        ]
        assert len(vnet_findings) == 0

    def test_incorrectly_named_keyvault(self, caf, empty_diagram):
        """A Key Vault named 'secrets-store' should fail naming checks."""
        empty_diagram.resources["secrets-store"] = _make_resource("key_vault", "secrets-store")
        report = caf.validate(empty_diagram)
        naming_findings = [
            f for f in report.findings
            if f.pillar == CafPrinciple.NAMING and "secrets-store" in f.affected_resources
        ]
        assert len(naming_findings) >= 1


class TestCafResourceOrganization:
    """Tests for CAF resource organization checks."""

    def test_resources_without_rg_boundary(self, caf, empty_diagram):
        """Resources not inside any resource group should generate org-related findings."""
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm-web-01")
        empty_diagram.resources["vm2"] = _make_resource("virtual_machine", "vm-api-01")
        empty_diagram.resources["db1"] = _make_resource("sql_database", "sqldb-main")
        report = caf.validate(empty_diagram)
        # Should have some findings (org, governance, etc)
        assert len(report.findings) >= 1

    def test_resources_inside_rg_boundary(self, caf, empty_diagram):
        """Resources inside a resource group boundary should be properly organized."""
        empty_diagram.boundaries["rg-app"] = BoundaryGroup(
            id="rg-app",
            boundary_type="resource_group",
            display_name="rg-app",
        )
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm-web-01", group_id="rg-app")
        report = caf.validate(empty_diagram)
        # Should have fewer/no org findings about missing RGs
        no_rg_findings = [
            f for f in report.findings
            if f.pillar == CafPrinciple.RESOURCE_ORGANIZATION and "resource group" in f.message.lower()
        ]
        assert len(no_rg_findings) == 0


class TestCafScoring:
    """Tests for CAF scoring logic."""

    def test_empty_diagram_score(self, caf, empty_diagram):
        """Empty diagram should return a valid score."""
        report = caf.validate(empty_diagram)
        assert 0 <= report.score <= 100
        assert report.framework == "CAF"

    def test_well_named_scores_higher(self, caf):
        """Properly named resources should score higher than poorly named ones."""
        bad = DiagramState(name="Bad")
        bad.resources["server1"] = _make_resource("virtual_machine", "server1")
        bad.resources["mydb"] = _make_resource("sql_database", "mydb")
        bad.resources["vault"] = _make_resource("key_vault", "vault")

        good = DiagramState(name="Good")
        good.resources["vm-web-01"] = _make_resource("virtual_machine", "vm-web-01")
        good.resources["sqldb-main"] = _make_resource("sql_database", "sqldb-main")
        good.resources["kv-app-01"] = _make_resource("key_vault", "kv-app-01")

        bad_report = caf.validate(bad)
        good_report = caf.validate(good)
        assert good_report.score >= bad_report.score


class TestCafNamingPrefixes:
    """Tests for the CAF_NAMING_PREFIXES constant."""

    def test_common_prefixes_exist(self):
        """Verify essential prefixes are defined."""
        assert CAF_NAMING_PREFIXES["virtual_machine"] == "vm-"
        assert CAF_NAMING_PREFIXES["app_service"] == "app-"
        assert CAF_NAMING_PREFIXES["key_vault"] == "kv-"
        assert CAF_NAMING_PREFIXES["virtual_network"] == "vnet-"
        assert CAF_NAMING_PREFIXES["storage_account"] == "st"
        assert CAF_NAMING_PREFIXES["kubernetes_service"] == "aks-"
