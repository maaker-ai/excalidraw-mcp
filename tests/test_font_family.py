"""Tests for font family support in text elements."""

from excalidraw_mcp.elements.text import create_text


def test_default_font_hand_drawn():
    """Default font is hand-drawn (fontFamily=1)."""
    text = create_text("id1", "Hello", x=0, y=0, font_size=16, width=50, height=22)
    assert text["fontFamily"] == 1  # hand-drawn


def test_code_font():
    """Code/monospace font."""
    text = create_text("id1", "code", x=0, y=0, font_size=16, width=50, height=22,
                       font_family="code")
    assert text["fontFamily"] == 3  # monospace


def test_normal_font():
    """Normal/sans-serif font."""
    text = create_text("id1", "normal", x=0, y=0, font_size=16, width=50, height=22,
                       font_family="normal")
    assert text["fontFamily"] == 2  # sans-serif
