"""Tests for line element creation utility."""

from excalidraw_mcp.elements.lines import create_line


def test_create_line_basic():
    """Basic line creation."""
    line = create_line(0, 0, 100, 0)
    assert line["type"] == "line"
    assert line["x"] == 0
    assert line["y"] == 0
    assert line["points"] == [[0, 0], [100, 0]]


def test_create_line_diagonal():
    """Diagonal line."""
    line = create_line(10, 20, 110, 120)
    assert line["points"] == [[0, 0], [100, 100]]


def test_create_line_dashed():
    """Dashed line style."""
    line = create_line(0, 0, 50, 0, stroke_style="dashed")
    assert line["strokeStyle"] == "dashed"


def test_create_line_custom_color():
    """Custom stroke color."""
    line = create_line(0, 0, 50, 0, stroke_color="#ff0000")
    assert line["strokeColor"] == "#ff0000"
