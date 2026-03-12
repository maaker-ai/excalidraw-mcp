"""Test theme support."""
import json
import tempfile
import os

from excalidraw_mcp.utils.file_io import save_excalidraw, load_excalidraw


def test_dark_theme_background():
    """Dark theme should set dark background color."""
    from excalidraw_mcp.elements.text import create_labeled_shape

    shape, text = create_labeled_shape(
        "rectangle", id="s1", label="Test", x=0, y=0,
    )

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw([shape, text], path, theme="dark")
        data = load_excalidraw(path)
        bg = data.get("appState", {}).get("viewBackgroundColor", "")
        assert bg == "#1e1e1e" or bg.startswith("#1") or bg.startswith("#2")
    finally:
        os.unlink(path)


def test_light_theme_background():
    """Light theme (default) should have white background."""
    from excalidraw_mcp.elements.text import create_labeled_shape

    shape, text = create_labeled_shape(
        "rectangle", id="s1", label="Test", x=0, y=0,
    )

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw([shape, text], path)
        data = load_excalidraw(path)
        bg = data.get("appState", {}).get("viewBackgroundColor", "#ffffff")
        assert bg == "#ffffff"
    finally:
        os.unlink(path)
