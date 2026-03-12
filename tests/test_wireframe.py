"""Tests for wireframe tool."""

import os
from excalidraw_mcp.tools.wireframe import create_wireframe_elements


def test_wireframe_basic():
    """Basic wireframe with components."""
    components = [
        {"type": "header", "label": "My App"},
        {"type": "text", "label": "Welcome to the app"},
        {"type": "button", "label": "Get Started"},
        {"type": "input", "label": "Email"},
    ]
    elements = create_wireframe_elements(components)
    assert len(elements) > 0

    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 3  # header, button, input are rectangles


def test_wireframe_phone_frame():
    """Wireframe with phone frame."""
    components = [
        {"type": "header", "label": "Mobile App"},
        {"type": "button", "label": "Login"},
    ]
    elements = create_wireframe_elements(components, device="phone")
    assert len(elements) > 0
    # Phone frame adds an outer rectangle
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 3  # frame + components


def test_wireframe_save(tmp_path):
    """Wireframe saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    components = [
        {"type": "header", "label": "Test"},
        {"type": "text", "label": "Hello"},
    ]
    elements = create_wireframe_elements(components, title="Login Screen")
    path = str(tmp_path / "wireframe.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
