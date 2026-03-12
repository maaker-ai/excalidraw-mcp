"""Tests for Unicode text width estimation."""

from excalidraw_mcp.elements.text import estimate_text_width


def test_ascii_width():
    """ASCII text width estimation."""
    w = estimate_text_width("Hello", 20)
    assert 40 < w < 80  # ~11px per char at 20px


def test_cjk_width():
    """CJK text is wider than ASCII."""
    ascii_w = estimate_text_width("ABCDE", 20)
    cjk_w = estimate_text_width("你好世界呀", 20)
    assert cjk_w > ascii_w  # 5 CJK chars should be wider than 5 ASCII


def test_mixed_width():
    """Mixed ASCII + CJK text."""
    w = estimate_text_width("Hello 你好", 20)
    pure_ascii = estimate_text_width("Hello ", 20)
    pure_cjk = estimate_text_width("你好", 20)
    # Mixed should be close to sum of parts
    assert w > pure_ascii


def test_emoji_width():
    """Emoji characters should be treated as wide."""
    w = estimate_text_width("🚀🎉", 20)
    assert w > 20  # emojis should have significant width


def test_empty_string():
    """Empty string has minimal width."""
    w = estimate_text_width("", 20)
    assert w >= 0
