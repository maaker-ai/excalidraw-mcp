"""Tests for radar/spider chart tool."""

import os
from excalidraw_mcp.tools.radar import create_radar_elements


def test_radar_basic():
    """Basic radar chart with axes and values."""
    axes = ["Speed", "Power", "Range", "Accuracy", "Defense"]
    values = [0.8, 0.6, 0.9, 0.7, 0.5]
    elements = create_radar_elements(axes, values)
    assert len(elements) > 0

    # Should have lines for axes
    lines = [e for e in elements if e["type"] == "line"]
    assert len(lines) >= 5  # one per axis

    # Should have text labels
    texts = [e for e in elements if e["type"] == "text"]
    assert len(texts) >= 5


def test_radar_multiple_series():
    """Radar with multiple value sets."""
    axes = ["A", "B", "C", "D"]
    series = [
        {"label": "Team 1", "values": [0.8, 0.6, 0.7, 0.9]},
        {"label": "Team 2", "values": [0.5, 0.9, 0.4, 0.7]},
    ]
    elements = create_radar_elements(axes, series=series)
    assert len(elements) > 0


def test_radar_save(tmp_path):
    """Radar chart saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    axes = ["X", "Y", "Z"]
    values = [0.5, 0.7, 0.3]
    elements = create_radar_elements(axes, values, title="Skills")
    path = str(tmp_path / "radar.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
