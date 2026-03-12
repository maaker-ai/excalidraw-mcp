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


def test_route_unknown():
    """Unknown diagram type returns error."""
    result = route_diagram(
        diagram_type="unknown_type",
        data={},
    )
    assert "unknown" in result.lower() or "not supported" in result.lower()
