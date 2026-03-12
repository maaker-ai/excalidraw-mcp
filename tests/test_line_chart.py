"""Tests for line chart tool."""

import os
from excalidraw_mcp.tools.line_chart import create_line_chart_elements


def test_line_chart_basic():
    """Basic line chart with single series."""
    series = [
        {"label": "Revenue", "points": [10, 25, 18, 30, 42]}
    ]
    x_labels = ["Jan", "Feb", "Mar", "Apr", "May"]
    elements = create_line_chart_elements(series, x_labels)
    assert len(elements) > 0

    lines = [e for e in elements if e["type"] == "line"]
    assert len(lines) >= 4  # 4 line segments for 5 points

    texts = [e for e in elements if e["type"] == "text"]
    assert len(texts) >= 5  # x-axis labels


def test_line_chart_multi_series():
    """Line chart with multiple series."""
    series = [
        {"label": "Revenue", "points": [10, 20, 30]},
        {"label": "Costs", "points": [15, 12, 25]},
    ]
    x_labels = ["Q1", "Q2", "Q3"]
    elements = create_line_chart_elements(series, x_labels)

    lines = [e for e in elements if e["type"] == "line"]
    # 2 segments per series × 2 series = 4 data lines + 2 axis lines
    assert len(lines) >= 6


def test_line_chart_save(tmp_path):
    """Line chart saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    series = [{"label": "A", "points": [5, 10, 8]}]
    elements = create_line_chart_elements(series, ["X", "Y", "Z"], title="Trend")
    path = str(tmp_path / "line-chart.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
