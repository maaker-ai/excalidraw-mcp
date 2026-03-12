"""Tests for bar chart tool."""

import os
from excalidraw_mcp.tools.bar_chart import create_bar_elements


def test_bar_basic():
    """Basic bar chart."""
    bars = [
        {"label": "Jan", "value": 100},
        {"label": "Feb", "value": 150},
        {"label": "Mar", "value": 80},
    ]
    elements = create_bar_elements(bars)
    assert len(elements) > 0

    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 3  # one per bar


def test_bar_colors():
    """Bars with custom colors."""
    bars = [
        {"label": "A", "value": 50, "color": "blue"},
        {"label": "B", "value": 30, "color": "red"},
    ]
    elements = create_bar_elements(bars)
    rects = [e for e in elements if e["type"] == "rectangle"]
    bgs = set(r.get("backgroundColor", "") for r in rects)
    assert len(bgs) >= 2


def test_bar_save(tmp_path):
    """Bar chart saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    bars = [{"label": "X", "value": 42}]
    elements = create_bar_elements(bars, title="Revenue")
    path = str(tmp_path / "bar.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
