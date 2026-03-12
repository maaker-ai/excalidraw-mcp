"""Tests for tool listing/help."""

from excalidraw_mcp.tools.help import get_available_diagrams


def test_list_all_diagrams():
    """Should list all available diagram types."""
    diagrams = get_available_diagrams()
    assert len(diagrams) >= 15  # We have 15+ diagram tools

    # Check some expected entries
    names = [d["name"] for d in diagrams]
    assert "flowchart" in names
    assert "sequence" in names
    assert "mindmap" in names
    assert "timeline" in names


def test_diagram_info_structure():
    """Each diagram entry has required fields."""
    diagrams = get_available_diagrams()
    for d in diagrams:
        assert "name" in d
        assert "description" in d
        assert "tool" in d
