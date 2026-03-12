"""Tests for unified create_diagram tool."""

import json
import os
from excalidraw_mcp.tools.unified import route_diagram


def test_route_flowchart(tmp_path):
    """Route to flowchart tool."""
    path = str(tmp_path / "test.excalidraw")
    result = route_diagram(
        diagram_type="flowchart",
        data={
            "nodes": [{"label": "A"}, {"label": "B"}],
            "edges": [{"from": "A", "to": "B"}],
        },
        output_path=path,
    )
    assert os.path.exists(path)
    assert "saved" in result.lower() or "flowchart" in result.lower()


def test_route_sequence(tmp_path):
    """Route to sequence diagram."""
    path = str(tmp_path / "test.excalidraw")
    result = route_diagram(
        diagram_type="sequence",
        data={
            "participants": ["Alice", "Bob"],
            "messages": [{"from": "Alice", "to": "Bob", "label": "Hello"}],
        },
        output_path=path,
    )
    assert os.path.exists(path)


def test_route_line_chart(tmp_path):
    """Route to line chart tool."""
    path = str(tmp_path / "test.excalidraw")
    result = route_diagram(
        diagram_type="line_chart",
        data={
            "series": [{"label": "Sales", "points": [10, 20, 30]}],
            "x_labels": ["Q1", "Q2", "Q3"],
        },
        output_path=path,
    )
    assert os.path.exists(path)
    assert "saved" in result.lower()


def test_route_decision_tree(tmp_path):
    """Route to decision tree tool."""
    path = str(tmp_path / "test.excalidraw")
    result = route_diagram(
        diagram_type="decision_tree",
        data={
            "nodes": [
                {"id": "q1", "label": "Yes?", "type": "decision"},
                {"id": "a1", "label": "Done", "type": "outcome"},
            ],
            "edges": [{"from": "q1", "to": "a1", "label": "Yes"}],
        },
        output_path=path,
    )
    assert os.path.exists(path)
    assert "saved" in result.lower()


def test_route_table(tmp_path):
    """Route to table tool."""
    path = str(tmp_path / "test.excalidraw")
    result = route_diagram(
        diagram_type="table",
        data={
            "headers": ["Name", "Age"],
            "rows": [["Alice", "30"], ["Bob", "25"]],
        },
        output_path=path,
    )
    assert os.path.exists(path)


def test_route_bar_chart(tmp_path):
    """Route to bar chart tool."""
    path = str(tmp_path / "test.excalidraw")
    result = route_diagram(
        diagram_type="bar_chart",
        data={
            "bars": [{"label": "A", "value": 10}, {"label": "B", "value": 20}],
        },
        output_path=path,
    )
    assert os.path.exists(path)


def test_route_radar(tmp_path):
    """Route to radar chart tool."""
    path = str(tmp_path / "test.excalidraw")
    result = route_diagram(
        diagram_type="radar_chart",
        data={
            "axes": ["Speed", "Power", "Range"],
            "values": [0.8, 0.6, 0.9],
        },
        output_path=path,
    )
    assert os.path.exists(path)


def test_route_unknown():
    """Unknown diagram type returns error."""
    result = route_diagram(
        diagram_type="unknown_type",
        data={},
    )
    assert "unknown" in result.lower() or "not supported" in result.lower()
