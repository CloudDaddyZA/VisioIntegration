"""Unit tests for the Mermaid rendering engine."""

import pytest

from visio_mcp.mermaid_engine import MermaidEngine
from visio_mcp.models import (
    BoundaryGroup,
    Connection,
    DiagramResource,
    DiagramState,
    Position,
)


@pytest.fixture
def engine():
    return MermaidEngine()


@pytest.fixture
def simple_diagram():
    state = DiagramState(name="Test Architecture")
    state.boundaries["rg-app"] = BoundaryGroup(
        id="rg-app",
        boundary_type="resource_group",
        display_name="rg-app",
    )
    state.boundaries["vnet-main"] = BoundaryGroup(
        id="vnet-main",
        boundary_type="vnet",
        display_name="vnet-main",
        parent_id="rg-app",
    )
    state.resources["vm-web-01"] = DiagramResource(
        id="vm-web-01",
        resource_type="virtual_machine",
        display_name="vm-web-01",
        position=Position(x=4.0, y=4.0),
        group_id="vnet-main",
    )
    state.resources["sqldb-main"] = DiagramResource(
        id="sqldb-main",
        resource_type="sql_database",
        display_name="sqldb-main",
        position=Position(x=4.0, y=8.0),
        group_id="rg-app",
    )
    state.connections["c1"] = Connection(
        id="c1",
        source_id="vm-web-01",
        target_id="sqldb-main",
        label="SQL",
        style="solid",
    )
    return state


def test_render_text_has_flowchart_header(engine, simple_diagram):
    text = engine.render_text(simple_diagram)
    assert "flowchart TB" in text
    assert "title: Test Architecture" in text


def test_boundaries_rendered_as_subgraphs(engine, simple_diagram):
    text = engine.render_text(simple_diagram)
    assert text.count("subgraph") == 2
    assert "end" in text
    # nested vnet appears after the rg subgraph opens
    assert "rg_app" in text or "rg-app".replace("-", "_") in text


def test_resources_rendered_as_nodes(engine, simple_diagram):
    text = engine.render_text(simple_diagram)
    assert "vm-web-01" in text
    assert "sqldb-main" in text
    assert "Virtual Machine" in text


def test_connection_rendered_as_edge(engine, simple_diagram):
    text = engine.render_text(simple_diagram)
    assert "-->|SQL|" in text


def test_dashed_connection_uses_dotted_link(engine):
    state = DiagramState(name="Dash")
    state.resources["a"] = DiagramResource(id="a", resource_type="virtual_machine", display_name="A")
    state.resources["b"] = DiagramResource(id="b", resource_type="sql_database", display_name="B")
    state.connections["c"] = Connection(id="c", source_id="a", target_id="b", style="dashed")
    text = engine.render_text(state)
    assert "-.->" in text


def test_classdefs_emitted(engine, simple_diagram):
    text = engine.render_text(simple_diagram)
    assert "classDef" in text


def test_empty_diagram(engine):
    state = DiagramState(name="Empty")
    text = engine.render_text(state)
    assert "flowchart TB" in text


def test_render_writes_file(engine, simple_diagram, tmp_path):
    out = str(tmp_path / "diagram.mmd")
    result = engine.render(simple_diagram, out)
    assert result.endswith(".mmd")
    content = open(result, encoding="utf-8").read()
    assert "flowchart TB" in content


def test_ungrouped_resources_top_level(engine):
    state = DiagramState(name="Loose")
    state.resources["lone"] = DiagramResource(
        id="lone", resource_type="storage_account", display_name="stmain"
    )
    text = engine.render_text(state)
    assert "stmain" in text
    assert "subgraph" not in text
