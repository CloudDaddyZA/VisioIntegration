"""Unit tests for the Draw.io rendering engine."""

import os
import tempfile
import xml.etree.ElementTree as ET

import pytest

from visio_mcp.models import (
    BoundaryGroup,
    Connection,
    DiagramResource,
    DiagramState,
    Position,
    Size,
)
from visio_mcp.drawio_engine import DrawioEngine


@pytest.fixture
def engine():
    return DrawioEngine()


@pytest.fixture
def tmp_path_drawio(tmp_path):
    return str(tmp_path / "test_output.drawio")


@pytest.fixture
def simple_diagram():
    state = DiagramState(name="Test Architecture")
    state.resources["vm-web-01"] = DiagramResource(
        id="vm-web-01",
        resource_type="virtual_machine",
        display_name="vm-web-01",
        position=Position(x=4.0, y=4.0),
    )
    state.resources["sqldb-main"] = DiagramResource(
        id="sqldb-main",
        resource_type="sql_database",
        display_name="sqldb-main",
        position=Position(x=4.0, y=8.0),
    )
    state.connections["c1"] = Connection(
        id="c1",
        source_id="vm-web-01",
        target_id="sqldb-main",
        label="SQL queries",
    )
    state.boundaries["rg-app"] = BoundaryGroup(
        id="rg-app",
        boundary_type="resource_group",
        display_name="rg-app",
        position=Position(x=1.0, y=1.0),
        size=Size(width=10.0, height=12.0),
    )
    return state


def _render_xml(engine, state, tmp_path_drawio):
    """Helper to render and read back the XML."""
    engine.render(state, tmp_path_drawio)
    with open(tmp_path_drawio, "r", encoding="utf-8") as f:
        return f.read()


class TestDrawioXmlStructure:
    """Tests for the generated Draw.io XML structure."""

    def test_generates_valid_xml(self, engine, simple_diagram, tmp_path_drawio):
        """Engine should produce valid XML."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        root = ET.fromstring(xml_str)
        assert root.tag == "mxfile"

    def test_has_diagram_element(self, engine, simple_diagram, tmp_path_drawio):
        """Output should contain a <diagram> element."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        root = ET.fromstring(xml_str)
        diagrams = root.findall("diagram")
        assert len(diagrams) >= 1

    def test_has_mxgraph_model(self, engine, simple_diagram, tmp_path_drawio):
        """Output should contain an mxGraphModel."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        root = ET.fromstring(xml_str)
        model = root.find(".//mxGraphModel")
        assert model is not None

    def test_resources_rendered_as_cells(self, engine, simple_diagram, tmp_path_drawio):
        """Each resource should produce an mxCell."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        root = ET.fromstring(xml_str)
        cells = root.findall(".//mxCell")
        # Should have cells for resources + connections + boundaries + root/layer cells
        assert len(cells) >= 4  # At least root + layer + 2 resources

    def test_connection_rendered(self, engine, simple_diagram, tmp_path_drawio):
        """Connections should produce edge cells."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        root = ET.fromstring(xml_str)
        cells = root.findall(".//mxCell")
        edge_cells = [c for c in cells if c.get("edge") == "1"]
        assert len(edge_cells) >= 1

    def test_boundary_rendered(self, engine, simple_diagram, tmp_path_drawio):
        """Boundaries should produce container cells."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        assert "rg-app" in xml_str

    def test_diagram_name_in_output(self, engine, simple_diagram, tmp_path_drawio):
        """Diagram title should appear in the output."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        assert "Test Architecture" in xml_str


class TestDrawioRendering:
    """Tests for specific rendering behaviors."""

    def test_empty_diagram(self, engine, tmp_path_drawio):
        """Empty diagram should produce valid XML with no resource cells."""
        state = DiagramState(name="Empty")
        xml_str = _render_xml(engine, state, tmp_path_drawio)
        root = ET.fromstring(xml_str)
        assert root.tag == "mxfile"

    def test_resource_label_in_output(self, engine, simple_diagram, tmp_path_drawio):
        """Resource display names should appear in the XML."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        assert "vm-web-01" in xml_str
        assert "sqldb-main" in xml_str

    def test_connection_label_in_output(self, engine, simple_diagram, tmp_path_drawio):
        """Connection labels should appear in the XML."""
        xml_str = _render_xml(engine, simple_diagram, tmp_path_drawio)
        assert "SQL queries" in xml_str
