"""Tests for enhanced line chart features: data point markers and legend."""

from excalidraw_mcp.tools.line_chart import create_line_chart_elements


def test_line_chart_data_point_markers():
    """Line chart should have ellipse markers at each data point."""
    series = [
        {"label": "Revenue", "points": [10, 20, 30]}
    ]
    x_labels = ["Q1", "Q2", "Q3"]
    elements = create_line_chart_elements(series, x_labels)

    ellipses = [e for e in elements if e["type"] == "ellipse"]
    assert len(ellipses) >= 3  # one per data point


def test_line_chart_legend():
    """Multi-series line chart should have a legend."""
    series = [
        {"label": "Revenue", "points": [10, 20, 30]},
        {"label": "Costs", "points": [5, 15, 25]},
    ]
    x_labels = ["Q1", "Q2", "Q3"]
    elements = create_line_chart_elements(series, x_labels)

    texts = [e for e in elements if e["type"] == "text"]
    text_contents = [t.get("text", "") for t in texts]
    # Legend should contain series labels
    assert any("Revenue" in t for t in text_contents)
    assert any("Costs" in t for t in text_contents)


def test_single_series_no_legend():
    """Single series should not show legend."""
    series = [{"label": "A", "points": [1, 2, 3]}]
    x_labels = ["X", "Y", "Z"]
    elements = create_line_chart_elements(series, x_labels)

    texts = [e for e in elements if e["type"] == "text"]
    text_contents = [t.get("text", "") for t in texts]
    # Only axis labels, no legend "A" separate from axis
    # The legend rect should not exist for single series
    rects = [e for e in elements if e["type"] == "rectangle"]
    legend_rects = [r for r in rects if r.get("backgroundColor") is not None]
    # No legend box for single series
    assert len(legend_rects) == 0
