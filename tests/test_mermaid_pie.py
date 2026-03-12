"""Tests for Mermaid pie chart parsing."""

from excalidraw_mcp.tools.mermaid import parse_mermaid_pie


def test_parse_mermaid_pie_basic():
    """Parse a basic Mermaid pie chart."""
    text = """pie title Pets
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
"""
    slices, pie_title = parse_mermaid_pie(text)
    assert len(slices) == 3
    assert slices[0]["label"] == "Dogs"
    assert slices[0]["value"] == 386
    assert slices[1]["label"] == "Cats"
    assert pie_title == "Pets"


def test_parse_mermaid_pie_no_title():
    """Parse pie chart without title."""
    text = """pie
    "A" : 50
    "B" : 50
"""
    slices, pie_title = parse_mermaid_pie(text)
    assert len(slices) == 2
    assert pie_title is None


def test_mermaid_import_pie():
    """import_mermaid auto-detects pie chart."""
    import os
    from excalidraw_mcp.tools.mermaid import parse_mermaid_pie
    from excalidraw_mcp.tools.pie_chart import create_pie_elements
    from excalidraw_mcp.utils.file_io import save_excalidraw

    text = """pie title Revenue
    "Product" : 70
    "Service" : 30
"""
    slices, title = parse_mermaid_pie(text)
    elements = create_pie_elements(slices, title=title)
    assert len(elements) > 0

    lines = [e for e in elements if e["type"] == "line"]
    assert len(lines) >= 2  # dividing lines
