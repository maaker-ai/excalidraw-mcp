"""Tests for arrow routing improvements."""

from excalidraw_mcp.elements.arrows import create_arrow


def test_arrow_binding_points():
    """Arrow should have correct start/end binding fixedPoints."""
    start = {"id": "s1", "x": 0, "y": 0, "width": 100, "height": 50, "boundElements": []}
    end = {"id": "e1", "x": 300, "y": 0, "width": 100, "height": 50, "boundElements": []}

    result = create_arrow("a1", start, end)
    arrow = next(e for e in result if e["type"] == "arrow")

    # Arrow should go right: start from right edge (fixedPoint ~[1, 0.5])
    assert arrow["startBinding"]["fixedPoint"][0] > 0.5
    assert arrow["endBinding"]["fixedPoint"][0] < 0.5


def test_arrow_vertical_binding():
    """Vertical arrow should bind top/bottom."""
    start = {"id": "s1", "x": 0, "y": 0, "width": 100, "height": 50, "boundElements": []}
    end = {"id": "e1", "x": 0, "y": 200, "width": 100, "height": 50, "boundElements": []}

    result = create_arrow("a1", start, end)
    arrow = next(e for e in result if e["type"] == "arrow")

    # Arrow should go down: start from bottom (fixedPoint ~[0.5, 1])
    assert arrow["startBinding"]["fixedPoint"][1] > 0.5


def test_arrow_updates_bound_elements():
    """Arrow should update start/end shape's boundElements."""
    start = {"id": "s1", "x": 0, "y": 0, "width": 100, "height": 50, "boundElements": []}
    end = {"id": "e1", "x": 300, "y": 0, "width": 100, "height": 50, "boundElements": []}

    create_arrow("a1", start, end)

    # Both shapes should now list the arrow in their boundElements
    assert any(be["id"] == "a1" for be in start["boundElements"])
    assert any(be["id"] == "a1" for be in end["boundElements"])
