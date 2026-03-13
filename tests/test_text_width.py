"""Tests for text width estimation — ensure no clipping in Excalidraw."""

from excalidraw_mcp.elements.text import estimate_text_width


# Excalidraw's Excalifont (hand-drawn) renders wider than typical sans-serif.
# These minimum widths are measured from actual Excalidraw rendering at fontSize=20.
KNOWN_TEXTS = [
    # (text, fontSize, min_expected_width)
    ("200 Tests", 20, 105),
    ("28 Tool Modules", 20, 165),
    ("40 Test Files", 20, 140),
    ("25+ Diagram Types", 20, 190),
    ("Hello World", 20, 120),
    ("A", 20, 12),
    ("OK", 20, 24),
]


def test_width_not_underestimated():
    """Width estimates should not be smaller than actual Excalidraw rendering."""
    for text, fs, min_width in KNOWN_TEXTS:
        w = estimate_text_width(text, fs)
        assert w >= min_width, (
            f"Width underestimated for '{text}': got {w:.1f}, need >= {min_width}"
        )


def test_width_has_padding_margin():
    """Estimates should include some margin to prevent clipping."""
    # For typical ASCII text at fontSize=20, average should be >= 11px/char
    for text in ["Test", "Hello World", "Diagram Types", "Tool Modules"]:
        w = estimate_text_width(text, 20)
        avg = w / len(text)
        assert avg >= 10.5, (
            f"Average char width too narrow for '{text}': {avg:.1f}px/char"
        )
