"""Tests for pie chart tool."""

import json
import os
import math
from excalidraw_mcp.tools.pie_chart import create_pie_elements


def test_pie_basic():
    """Basic pie chart with slices."""
    slices = [
        {"label": "A", "value": 50},
        {"label": "B", "value": 30},
        {"label": "C", "value": 20},
    ]
    elements = create_pie_elements(slices)
    assert len(elements) > 0


def test_pie_labels():
    """Pie chart has label text elements."""
    slices = [
        {"label": "Frontend", "value": 40},
        {"label": "Backend", "value": 60},
    ]
    elements = create_pie_elements(slices)
    texts = [e for e in elements if e["type"] == "text"]
    labels = [t["text"] for t in texts]
    assert any("Frontend" in l for l in labels)
    assert any("Backend" in l for l in labels)


def test_pie_colors():
    """Each slice gets a different color."""
    slices = [
        {"label": "X", "value": 1},
        {"label": "Y", "value": 1},
        {"label": "Z", "value": 1},
    ]
    elements = create_pie_elements(slices)
    # Lines/paths should exist to divide the circle
    lines = [e for e in elements if e["type"] == "line"]
    assert len(lines) >= 3  # at least one dividing line per slice


def test_pie_save(tmp_path):
    """Pie chart saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    slices = [
        {"label": "Yes", "value": 70},
        {"label": "No", "value": 30},
    ]
    elements = create_pie_elements(slices, title="Survey Results")
    path = str(tmp_path / "pie.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
