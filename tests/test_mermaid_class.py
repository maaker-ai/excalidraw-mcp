"""Tests for Mermaid class diagram parsing."""

from excalidraw_mcp.tools.mermaid import parse_mermaid_class


def test_parse_class_basic():
    """Parse basic class definition."""
    text = """classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    """
    classes, rels = parse_mermaid_class(text)
    assert len(classes) == 1
    assert classes[0]["name"] == "Animal"
    assert "+String name" in classes[0]["attributes"]
    assert "+makeSound()" in classes[0]["methods"]


def test_parse_class_inheritance():
    """Parse inheritance relationship."""
    text = """classDiagram
    Animal <|-- Dog
    Animal <|-- Cat
    """
    classes, rels = parse_mermaid_class(text)
    assert len(rels) >= 2
    # Dog inherits from Animal
    assert any(r["from"] == "Dog" and r["to"] == "Animal" and r["type"] == "inheritance" for r in rels)


def test_parse_class_association():
    """Parse association relationships."""
    text = """classDiagram
    Customer --> Order
    Order *-- LineItem
    """
    classes, rels = parse_mermaid_class(text)
    assert len(rels) >= 2


def test_parse_class_with_label():
    """Parse relationship with label."""
    text = """classDiagram
    Customer "1" --> "*" Order : places
    """
    classes, rels = parse_mermaid_class(text)
    assert len(rels) >= 1
    assert any(r.get("label") == "places" for r in rels)
