"""Comprehensive integration test — verifies all diagram types end-to-end."""

import json
import os
from excalidraw_mcp.tools.unified import route_diagram


ALL_DIAGRAM_CONFIGS = [
    ("flowchart", {"nodes": [{"label": "A"}, {"label": "B"}], "edges": [{"from": "A", "to": "B"}]}),
    ("sequence", {"participants": ["Alice", "Bob"], "messages": [{"from": "Alice", "to": "Bob", "label": "Hi"}]}),
    ("mindmap", {"label": "Root", "children": [{"label": "A"}, {"label": "B"}]}),
    ("er_diagram", {"entities": [{"name": "User", "attributes": ["id", "name"]}], "relationships": []}),
    ("class_diagram", {"classes": [{"name": "Foo", "attributes": ["+id: int"], "methods": ["+run()"]}], "relationships": []}),
    ("state_diagram", {"states": [{"name": "Idle"}], "transitions": []}),
    ("timeline", {"events": [{"label": "Launch", "start": 0, "end": 3}]}),
    ("pie_chart", {"slices": [{"label": "A", "value": 60}, {"label": "B", "value": 40}]}),
    ("kanban", {"columns": [{"name": "Todo", "cards": ["Task 1"]}]}),
    ("network", {"nodes": [{"id": "s1", "label": "Server", "type": "server"}], "links": []}),
    ("quadrant", {"items": [{"label": "X", "x": 0.5, "y": 0.5}], "x_label": "Effort", "y_label": "Impact"}),
    ("user_journey", {"steps": [{"label": "Visit", "emotion": "happy", "description": "Opens site"}]}),
    ("wireframe", {"components": [{"type": "header", "text": "Title"}], "device": "phone"}),
    ("org_chart", {"label": "CEO", "children": [{"label": "CTO"}, {"label": "CFO"}]}),
    ("swot", {"strengths": ["Fast"], "weaknesses": ["Small"], "opportunities": ["Growth"], "threats": ["Competition"]}),
    ("architecture", {"layers": [{"name": "Frontend", "components": [{"label": "App"}]}], "connections": []}),
    ("table", {"headers": ["Name", "Age"], "rows": [["Alice", "30"]]}),
    ("radar_chart", {"axes": ["A", "B", "C"], "values": [0.5, 0.7, 0.3]}),
    ("bar_chart", {"bars": [{"label": "Q1", "value": 100}, {"label": "Q2", "value": 150}]}),
    ("line_chart", {"series": [{"label": "Sales", "points": [10, 20, 30]}], "x_labels": ["Jan", "Feb", "Mar"]}),
    ("decision_tree", {"nodes": [{"id": "q1", "label": "Yes?", "type": "decision"}, {"id": "a1", "label": "Done", "type": "outcome"}], "edges": [{"from": "q1", "to": "a1", "label": "Yes"}]}),
]


def test_all_diagram_types_generate(tmp_path):
    """Every supported diagram type should generate a valid .excalidraw file."""
    for dtype, data in ALL_DIAGRAM_CONFIGS:
        path = str(tmp_path / f"{dtype}.excalidraw")
        result = route_diagram(dtype, data, title=f"Test {dtype}", output_path=path)
        assert os.path.exists(path), f"Failed to create file for {dtype}: {result}"

        with open(path) as f:
            doc = json.load(f)
        assert "elements" in doc, f"{dtype}: missing 'elements' key"
        assert len(doc["elements"]) > 0, f"{dtype}: empty elements"
        assert doc["type"] == "excalidraw", f"{dtype}: wrong doc type"


def test_all_diagram_types_count():
    """We should have at least 21 diagram type configs tested."""
    assert len(ALL_DIAGRAM_CONFIGS) >= 21
