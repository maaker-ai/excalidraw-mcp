"""Tests for quadrant chart tool."""

import os
from excalidraw_mcp.tools.quadrant import create_quadrant_elements


def test_quadrant_basic():
    """Basic quadrant chart with items."""
    items = [
        {"label": "Feature A", "x": 0.8, "y": 0.9},
        {"label": "Feature B", "x": 0.2, "y": 0.3},
        {"label": "Feature C", "x": 0.7, "y": 0.2},
    ]
    elements = create_quadrant_elements(
        items,
        x_label="Effort", y_label="Impact",
        quadrant_labels=["Quick Wins", "Major Projects", "Fill-Ins", "Thankless Tasks"],
    )
    assert len(elements) > 0

    # Should have lines for axes
    lines = [e for e in elements if e["type"] == "line"]
    assert len(lines) >= 2  # x and y axes

    # Should have text for items and labels
    texts = [e for e in elements if e["type"] == "text"]
    assert len(texts) >= 3  # at least the 3 items


def test_quadrant_labels():
    """Quadrant labels appear in output."""
    items = [{"label": "X", "x": 0.5, "y": 0.5}]
    elements = create_quadrant_elements(
        items,
        x_label="Cost", y_label="Value",
        quadrant_labels=["Q1", "Q2", "Q3", "Q4"],
    )
    texts = [e for e in elements if e["type"] == "text"]
    text_contents = [t["text"] for t in texts]
    assert any("Q1" in t for t in text_contents)


def test_quadrant_save(tmp_path):
    """Quadrant chart saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    items = [{"label": "A", "x": 0.5, "y": 0.5}]
    elements = create_quadrant_elements(items)
    path = str(tmp_path / "quadrant.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
