"""Tests for advanced Mermaid parsing features."""

from excalidraw_mcp.tools.mermaid import parse_mermaid_flowchart


def test_parse_style_class():
    """Style and class declarations should not crash."""
    text = """graph LR
    A[Start] --> B[End]
    style A fill:#f9f,stroke:#333
    classDef highlight fill:#ff0
    class B highlight
    """
    nodes, edges = parse_mermaid_flowchart(text)
    assert len(nodes) >= 2
    assert len(edges) >= 1


def test_parse_click_and_link():
    """Click and link declarations should not crash."""
    text = """graph LR
    A[Start] --> B[End]
    click A "https://example.com"
    """
    nodes, edges = parse_mermaid_flowchart(text)
    assert len(nodes) >= 2


def test_parse_long_labels():
    """Nodes with long multi-word labels."""
    text = """graph TB
    A[This is a very long label] --> B[Another long label here]
    """
    nodes, edges = parse_mermaid_flowchart(text)
    assert any(n["label"] == "This is a very long label" for n in nodes)


def test_parse_special_chars_in_labels():
    """Labels with special characters."""
    text = """graph LR
    A["User's Data"] --> B["API (v2.0)"]
    """
    nodes, edges = parse_mermaid_flowchart(text)
    assert len(nodes) >= 2


def test_parse_direction_td():
    """TD direction should map to TB."""
    text = """graph TD
    A --> B
    """
    nodes, edges = parse_mermaid_flowchart(text)
    assert len(nodes) >= 2
