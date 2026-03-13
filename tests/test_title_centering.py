"""Tests for title centering across all diagram types."""

import json
from excalidraw_mcp.tools.unified import route_diagram


def _get_title_and_bounds(path: str):
    """Extract title and content bounding box from a generated file."""
    with open(path) as f:
        doc = json.load(f)

    elements = doc["elements"]
    title_el = None
    for e in elements:
        if e["type"] == "text" and e.get("fontSize", 0) >= 24:
            title_el = e
            break

    if not title_el:
        return None, None

    non_title = [e for e in elements if e is not title_el and "x" in e and "width" in e]
    if not non_title:
        return title_el, None

    min_x = min(e["x"] for e in non_title)
    max_x = max(e["x"] + e["width"] for e in non_title)
    return title_el, (min_x, max_x)


def _assert_title_centered(path: str, diagram_name: str):
    """Assert title is roughly centered over diagram content."""
    title_el, bounds = _get_title_and_bounds(path)
    assert title_el is not None, f"{diagram_name}: no title element found"
    assert bounds is not None, f"{diagram_name}: no content elements found"

    min_x, max_x = bounds
    content_center = (min_x + max_x) / 2
    title_center = title_el["x"] + title_el["width"] / 2

    content_width = max_x - min_x
    tolerance = max(content_width * 0.3, 50)  # at least 50px tolerance
    assert abs(title_center - content_center) < tolerance, (
        f"{diagram_name}: title not centered. "
        f"title_center={title_center:.1f}, content_center={content_center:.1f}, "
        f"diff={abs(title_center - content_center):.1f}, tolerance={tolerance:.1f}"
    )


DIAGRAM_CONFIGS = [
    ("flowchart", {"nodes": [{"label": "Start"}, {"label": "Process"}, {"label": "End"}],
                   "edges": [{"from": "Start", "to": "Process"}, {"from": "Process", "to": "End"}]}),
    ("sequence", {"participants": ["Alice", "Bob", "Charlie"],
                  "messages": [{"from": "Alice", "to": "Charlie", "label": "Hi"}]}),
    ("mindmap", {"label": "Root", "children": [{"label": "A"}, {"label": "B"}, {"label": "C"}]}),
    ("er_diagram", {"entities": [{"name": "User", "attributes": ["id", "name"]},
                                 {"name": "Order", "attributes": ["id"]}], "relationships": []}),
    ("class_diagram", {"classes": [{"name": "Foo", "attributes": ["+id"], "methods": ["+run()"]},
                                   {"name": "Bar", "attributes": ["+x"], "methods": []}], "relationships": []}),
    ("state_diagram", {"states": [{"name": "Idle"}, {"name": "Run"}, {"name": "Done"}],
                       "transitions": [{"from": "Idle", "to": "Run", "label": "go"}]}),
    ("timeline", {"events": [{"label": "Phase 1", "start": 0, "end": 3},
                             {"label": "Phase 2", "start": 2, "end": 6}]}),
    ("kanban", {"columns": [{"name": "Todo", "cards": ["A"]}, {"name": "Done", "cards": ["B"]}]}),
    ("network", {"nodes": [{"id": "s1", "label": "Server", "type": "server"},
                           {"id": "db", "label": "DB", "type": "database"}], "links": []}),
    ("user_journey", {"steps": [{"label": "Visit", "emotion": "happy", "description": "Opens"},
                                {"label": "Buy", "emotion": "neutral", "description": "Pays"}]}),
    ("org_chart", {"label": "CEO", "children": [{"label": "CTO"}, {"label": "CFO"}]}),
    ("table", {"headers": ["Name", "Age", "City"], "rows": [["Alice", "30", "NYC"]]}),
]


def test_all_titles_centered(tmp_path):
    """Every diagram type should center its title over content."""
    failures = []
    for dtype, data in DIAGRAM_CONFIGS:
        path = str(tmp_path / f"{dtype}.excalidraw")
        route_diagram(dtype, data, title="Test Title Here", output_path=path)
        try:
            _assert_title_centered(path, dtype)
        except AssertionError as e:
            failures.append(str(e))

    assert not failures, f"Title centering failures:\n" + "\n".join(failures)
