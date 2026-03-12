"""Test entity-relationship diagram generation."""
import json
import os
import tempfile


def test_er_basic():
    """Basic ER diagram with 2 entities and 1 relationship."""
    from excalidraw_mcp.tools.er_diagram import create_er_elements

    entities = [
        {"name": "User", "attributes": ["id", "name", "email"]},
        {"name": "Post", "attributes": ["id", "title", "content"]},
    ]
    relationships = [
        {"from": "User", "to": "Post", "label": "writes", "from_cardinality": "1", "to_cardinality": "N"}
    ]

    elements = create_er_elements(entities, relationships)
    assert len(elements) > 0

    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 2  # at least entity headers

    texts = [e for e in elements if e["type"] == "text"]
    text_values = [t["text"] for t in texts]
    assert "User" in text_values
    assert "Post" in text_values


def test_er_attributes_displayed():
    """Entity attributes should appear as text."""
    from excalidraw_mcp.tools.er_diagram import create_er_elements

    entities = [
        {"name": "User", "attributes": ["id (PK)", "name", "email"]},
    ]

    elements = create_er_elements(entities, [])
    texts = [e for e in elements if e["type"] == "text"]
    text_values = [t["text"] for t in texts]
    assert any("id (PK)" in v for v in text_values)
    assert any("name" in v for v in text_values)
    assert any("email" in v for v in text_values)


def test_er_relationship_arrow():
    """Relationships should create arrows between entities."""
    from excalidraw_mcp.tools.er_diagram import create_er_elements

    entities = [
        {"name": "User", "attributes": ["id"]},
        {"name": "Post", "attributes": ["id"]},
    ]
    relationships = [
        {"from": "User", "to": "Post", "label": "has many"}
    ]

    elements = create_er_elements(entities, relationships)
    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) >= 1


def test_er_save():
    """ER diagram should save to valid .excalidraw file."""
    from excalidraw_mcp.tools.er_diagram import create_er_elements
    from excalidraw_mcp.utils.file_io import save_excalidraw, load_excalidraw

    entities = [
        {"name": "User", "attributes": ["id", "name"]},
        {"name": "Post", "attributes": ["id", "title"]},
    ]
    relationships = [
        {"from": "User", "to": "Post", "label": "writes"}
    ]

    elements = create_er_elements(entities, relationships)

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw(elements, path)
        data = load_excalidraw(path)
        assert data["type"] == "excalidraw"
        assert len(data["elements"]) > 0
    finally:
        os.unlink(path)
