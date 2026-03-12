"""Test mind map / tree layout."""
import json
import os
import tempfile


def test_mindmap_basic():
    """Basic mind map with root and 3 children."""
    from excalidraw_mcp.tools.mindmap import create_mindmap_elements

    root = {
        "label": "Main Topic",
        "children": [
            {"label": "Idea 1"},
            {"label": "Idea 2"},
            {"label": "Idea 3"},
        ]
    }

    elements = create_mindmap_elements(root)
    assert len(elements) > 0

    # Should have rectangles for nodes
    rects = [e for e in elements if e["type"] in ("rectangle", "ellipse")]
    assert len(rects) >= 4  # root + 3 children

    # Should have lines/arrows connecting
    connectors = [e for e in elements if e["type"] in ("arrow", "line")]
    assert len(connectors) == 3  # root to each child


def test_mindmap_nested():
    """Mind map with nested children."""
    from excalidraw_mcp.tools.mindmap import create_mindmap_elements

    root = {
        "label": "Root",
        "children": [
            {
                "label": "Branch 1",
                "children": [
                    {"label": "Leaf 1.1"},
                    {"label": "Leaf 1.2"},
                ]
            },
            {"label": "Branch 2"},
        ]
    }

    elements = create_mindmap_elements(root)
    rects = [e for e in elements if e["type"] in ("rectangle", "ellipse")]
    assert len(rects) >= 5  # root + 2 branches + 2 leaves

    connectors = [e for e in elements if e["type"] in ("arrow", "line")]
    assert len(connectors) == 4  # root->b1, root->b2, b1->l1.1, b1->l1.2


def test_mindmap_colors():
    """Each branch should get a distinct color."""
    from excalidraw_mcp.tools.mindmap import create_mindmap_elements

    root = {
        "label": "Center",
        "children": [
            {"label": "A"},
            {"label": "B"},
            {"label": "C"},
        ]
    }

    elements = create_mindmap_elements(root)
    rects = [e for e in elements if e["type"] in ("rectangle", "ellipse") and e.get("backgroundColor") != "transparent"]
    bg_colors = set(r["backgroundColor"] for r in rects)
    # Should have at least 2 distinct colors (root + branches)
    assert len(bg_colors) >= 2


def test_mindmap_save():
    """Mind map should save to valid .excalidraw file."""
    from excalidraw_mcp.tools.mindmap import create_mindmap_elements
    from excalidraw_mcp.utils.file_io import save_excalidraw, load_excalidraw

    root = {
        "label": "Test",
        "children": [{"label": "A"}, {"label": "B"}]
    }

    elements = create_mindmap_elements(root)

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw(elements, path)
        data = load_excalidraw(path)
        assert data["type"] == "excalidraw"
        assert len(data["elements"]) > 0
    finally:
        os.unlink(path)
