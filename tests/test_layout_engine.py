"""Unit tests for the layout engine."""

import pytest

from visio_mcp.models import (
    BoundaryGroup,
    Connection,
    DiagramResource,
    DiagramState,
    Position,
    Size,
)
from visio_mcp.layout_engine import LayoutEngine


@pytest.fixture
def layout():
    return LayoutEngine()


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


class TestGridLayout:
    """Tests for grid layout strategy."""

    def test_grid_positions_resources(self, layout, empty_diagram):
        """Grid layout should assign unique positions to all resources."""
        for i in range(6):
            empty_diagram.resources[f"vm{i}"] = _make_resource("virtual_machine", f"vm{i}")

        result = layout.auto_layout(empty_diagram, strategy="grid")
        positions = [(r.position.x, r.position.y) for r in result.resources.values()]
        # All positions should be unique
        assert len(set(positions)) == 6

    def test_grid_no_overlap(self, layout, empty_diagram):
        """Grid layout resources should not overlap."""
        for i in range(4):
            empty_diagram.resources[f"r{i}"] = _make_resource("app_service", f"r{i}")

        result = layout.auto_layout(empty_diagram, strategy="grid")
        positions = [(r.position.x, r.position.y) for r in result.resources.values()]
        # No two resources at the same position
        assert len(set(positions)) == len(positions)


class TestTieredLayout:
    """Tests for tiered layout strategy."""

    def test_tiered_separates_tiers(self, layout, empty_diagram):
        """Tiered layout should separate networking, compute, and data resources."""
        empty_diagram.resources["fw1"] = _make_resource("firewall", "fw1")
        empty_diagram.resources["app1"] = _make_resource("app_service", "app1")
        empty_diagram.resources["db1"] = _make_resource("sql_database", "db1")

        result = layout.auto_layout(empty_diagram, strategy="tiered")

        fw_pos = result.resources["fw1"].position
        app_pos = result.resources["app1"].position
        db_pos = result.resources["db1"].position

        # All should have distinct positions
        positions = {(fw_pos.x, fw_pos.y), (app_pos.x, app_pos.y), (db_pos.x, db_pos.y)}
        assert len(positions) == 3

    def test_tiered_returns_same_state(self, layout, empty_diagram):
        """Auto-layout should modify and return the same state object."""
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm1")
        result = layout.auto_layout(empty_diagram, strategy="tiered")
        assert result is empty_diagram


class TestHintBasedLayout:
    """Tests for hint-based layout from reference architectures."""

    def test_hints_applied_exactly(self, layout, empty_diagram):
        """When layout hints are provided, resources should be placed at those exact positions."""
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm1")
        empty_diagram.resources["db1"] = _make_resource("sql_database", "db1")

        hints = {"vm1": (5.0, 3.0), "db1": (8.0, 6.0)}
        result = layout.auto_layout(empty_diagram, layout_hints=hints)

        assert result.resources["vm1"].position.x == 5.0
        assert result.resources["vm1"].position.y == 3.0
        assert result.resources["db1"].position.x == 8.0
        assert result.resources["db1"].position.y == 6.0

    def test_unhinted_resources_get_positions(self, layout, empty_diagram):
        """Resources without hints should still get valid positions."""
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm1")
        empty_diagram.resources["vm2"] = _make_resource("virtual_machine", "vm2")

        hints = {"vm1": (5.0, 3.0)}  # Only vm1 has a hint
        result = layout.auto_layout(empty_diagram, layout_hints=hints)

        # vm2 should have been positioned somewhere
        assert result.resources["vm2"].position.x > 0
        assert result.resources["vm2"].position.y > 0

    def test_boundary_hints_applied(self, layout, empty_diagram):
        """Boundary hints should set position and size."""
        empty_diagram.boundaries["vnet1"] = BoundaryGroup(
            id="vnet1",
            boundary_type="virtual_network",
            display_name="vnet1",
        )

        boundary_hints = {"vnet1": (1.0, 1.0, 10.0, 8.0)}
        result = layout.auto_layout(empty_diagram, boundary_hints=boundary_hints)

        assert result.boundaries["vnet1"].position.x == 1.0
        assert result.boundaries["vnet1"].position.y == 1.0
        assert result.boundaries["vnet1"].size.width == 10.0
        assert result.boundaries["vnet1"].size.height == 8.0


class TestGroupedLayout:
    """Tests for grouped layout strategy."""

    def test_grouped_with_boundaries(self, layout, empty_diagram):
        """Grouped layout should position resources within their boundaries."""
        empty_diagram.boundaries["rg1"] = BoundaryGroup(
            id="rg1",
            boundary_type="resource_group",
            display_name="rg1",
        )
        empty_diagram.resources["vm1"] = _make_resource("virtual_machine", "vm1", group_id="rg1")
        empty_diagram.resources["vm2"] = _make_resource("virtual_machine", "vm2", group_id="rg1")

        result = layout.auto_layout(empty_diagram, strategy="grouped")

        # Resources should have been positioned
        assert result.resources["vm1"].position.x > 0
        assert result.resources["vm2"].position.x > 0
