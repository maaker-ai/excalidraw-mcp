"""Tests for SWOT analysis tool."""

import os
from excalidraw_mcp.tools.swot import create_swot_elements


def test_swot_basic():
    """Basic SWOT with all 4 quadrants."""
    data = {
        "strengths": ["Strong brand", "Loyal customers"],
        "weaknesses": ["High costs"],
        "opportunities": ["New market"],
        "threats": ["Competitor growth"],
    }
    elements = create_swot_elements(data)
    assert len(elements) > 0

    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 4  # 4 quadrant backgrounds

    texts = [e for e in elements if e["type"] == "text"]
    text_values = [t["text"] for t in texts]
    assert any("Strengths" in t for t in text_values)
    assert any("Weaknesses" in t for t in text_values)


def test_swot_empty_quadrants():
    """SWOT with some empty quadrants."""
    data = {
        "strengths": ["Brand"],
        "weaknesses": [],
        "opportunities": [],
        "threats": ["Competition"],
    }
    elements = create_swot_elements(data)
    assert len(elements) > 0


def test_swot_save(tmp_path):
    """SWOT saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    data = {
        "strengths": ["A"],
        "weaknesses": ["B"],
        "opportunities": ["C"],
        "threats": ["D"],
    }
    elements = create_swot_elements(data, title="SWOT Analysis")
    path = str(tmp_path / "swot.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
