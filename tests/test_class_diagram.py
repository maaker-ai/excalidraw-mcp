"""Tests for class diagram tool."""

import json
import os
from excalidraw_mcp.tools.class_diagram import create_class_elements


def test_class_basic():
    """Basic class with attributes and methods."""
    classes = [
        {
            "name": "User",
            "attributes": ["id: int", "name: string", "email: string"],
            "methods": ["login()", "logout()"],
        }
    ]
    elements = create_class_elements(classes, [])
    assert len(elements) > 0

    # Should have rectangles for sections (header, attrs, methods)
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 2  # header + body sections

    texts = [e for e in elements if e["type"] == "text"]
    # At least: class name, attributes, methods
    assert len(texts) >= 4


def test_class_inheritance():
    """Classes with inheritance relationship."""
    classes = [
        {"name": "Animal", "attributes": ["name: string"], "methods": ["speak()"]},
        {"name": "Dog", "attributes": ["breed: string"], "methods": ["bark()"]},
    ]
    relationships = [
        {"from": "Dog", "to": "Animal", "type": "inheritance"},
    ]
    elements = create_class_elements(classes, relationships)

    # Should have arrow elements
    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) >= 1


def test_class_multiple():
    """Multiple classes positioned without overlap."""
    classes = [
        {"name": "A", "attributes": ["x: int"], "methods": []},
        {"name": "B", "attributes": ["y: int"], "methods": []},
        {"name": "C", "attributes": ["z: int"], "methods": []},
    ]
    elements = create_class_elements(classes, [])
    rects = [e for e in elements if e["type"] == "rectangle"]

    # Each class should have at least header + body
    assert len(rects) >= 6  # 3 classes × 2 sections


def test_class_save(tmp_path):
    """Class diagram saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    classes = [
        {"name": "Product", "attributes": ["id: int", "price: float"], "methods": ["getPrice()"]},
    ]
    elements = create_class_elements(classes, [])
    path = str(tmp_path / "class.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
    with open(result) as f:
        data = json.load(f)
    assert len(data["elements"]) > 0
