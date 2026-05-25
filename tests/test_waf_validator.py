"""Unit tests for the WAF validator engine."""

import pytest

from visio_mcp.models import (
    BoundaryGroup,
    Connection,
    DiagramResource,
    DiagramState,
    Position,
    Severity,
    Size,
    ValidationFinding,
    WafPillar,
)
from visio_mcp.waf_validator import WafValidator


@pytest.fixture
def waf():
    return WafValidator()


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


class TestWafReliability:
    """Tests for WAF Reliability pillar checks."""

    def test_single_compute_no_lb_no_finding(self, waf, empty_diagram):
        """Single compute resource should not trigger load balancer finding."""
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm1")
        report = waf.validate(empty_diagram)
        lb_findings = [f for f in report.findings if "load balancer" in f.message.lower()]
        assert len(lb_findings) == 0

    def test_multiple_compute_no_lb_triggers_critical(self, waf, empty_diagram):
        """Multiple compute resources without a load balancer should be critical."""
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm1")
        empty_diagram.resources["vm2"] = _make_resource("virtual_machine", "vm2")
        report = waf.validate(empty_diagram)
        lb_findings = [f for f in report.findings if "load balancer" in f.message.lower()]
        assert len(lb_findings) == 1
        assert lb_findings[0].severity == Severity.CRITICAL

    def test_multiple_compute_with_lb_no_finding(self, waf, empty_diagram):
        """Multiple compute + load balancer should not trigger that finding."""
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm1")
        empty_diagram.resources["vm2"] = _make_resource("virtual_machine", "vm2")
        empty_diagram.resources["lb1"] = _make_resource("load_balancer", "lb1")
        report = waf.validate(empty_diagram)
        lb_findings = [f for f in report.findings if "load balancer" in f.message.lower()]
        assert len(lb_findings) == 0


class TestWafSecurity:
    """Tests for WAF Security pillar checks."""

    def test_database_without_private_endpoint(self, waf, empty_diagram):
        """Database without private endpoint should generate security finding."""
        empty_diagram.resources["db1"] = _make_resource("sql_database", "db1")
        report = waf.validate(empty_diagram)
        pe_findings = [f for f in report.findings if "private endpoint" in f.message.lower()]
        assert len(pe_findings) >= 1

    def test_database_with_private_endpoint_no_finding(self, waf, empty_diagram):
        """Database with private endpoint should not trigger that finding."""
        empty_diagram.resources["db1"] = _make_resource("sql_database", "db1")
        empty_diagram.resources["pe1"] = _make_resource("private_endpoint", "pe1")
        empty_diagram.connections["c1"] = Connection(
            id="c1", source_id="pe1", target_id="db1", label="private link"
        )
        report = waf.validate(empty_diagram)
        pe_findings = [
            f for f in report.findings
            if "private endpoint" in f.message.lower() and "db1" in f.affected_resources
        ]
        assert len(pe_findings) == 0


class TestWafScoring:
    """Tests for WAF scoring logic."""

    def test_empty_diagram_has_score(self, waf, empty_diagram):
        """Empty diagram should return a valid score."""
        report = waf.validate(empty_diagram)
        assert 0 <= report.score <= 100
        assert report.framework == "WAF"

    def test_well_architected_scores_higher(self, waf):
        """A well-architected diagram should score higher than a bare one."""
        bare = DiagramState(name="Bare")
        bare.resources["vm1"] = _make_resource("virtual_machine", "vm1")
        bare.resources["vm2"] = _make_resource("virtual_machine", "vm2")
        bare.resources["db1"] = _make_resource("sql_database", "db1")

        good = DiagramState(name="Good")
        good.resources["vm1"] = _make_resource("virtual_machine", "vm1")
        good.resources["vm2"] = _make_resource("virtual_machine", "vm2")
        good.resources["db1"] = _make_resource("sql_database", "db1")
        good.resources["lb1"] = _make_resource("load_balancer", "lb1")
        good.resources["pe1"] = _make_resource("private_endpoint", "pe1")
        good.resources["fw1"] = _make_resource("firewall", "fw1")
        good.resources["mon1"] = _make_resource("application_insights", "mon1")
        good.connections["c1"] = Connection(
            id="c1", source_id="pe1", target_id="db1", label="private"
        )

        bare_report = waf.validate(bare)
        good_report = waf.validate(good)
        assert good_report.score > bare_report.score


class TestWafFindingModel:
    """Tests for the ValidationFinding model with Severity enum."""

    def test_severity_enum_from_string(self):
        """String values should coerce to Severity enum members."""
        finding = ValidationFinding(
            severity="critical",
            pillar="Reliability",
            message="test",
            recommendation="fix it",
        )
        assert finding.severity == Severity.CRITICAL
        assert finding.severity.value == "critical"

    def test_invalid_severity_raises(self):
        """Invalid severity string should raise validation error."""
        with pytest.raises(Exception):
            ValidationFinding(
                severity="banana",
                pillar="Reliability",
                message="test",
                recommendation="fix it",
            )
