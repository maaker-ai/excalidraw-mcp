"""Tests for decision tree tool."""

import os
from excalidraw_mcp.tools.decision_tree import create_decision_tree_elements


def test_decision_tree_basic():
    """Basic decision tree with yes/no branches."""
    nodes = [
        {"id": "q1", "label": "Is it raining?", "type": "decision"},
        {"id": "a1", "label": "Take umbrella", "type": "outcome"},
        {"id": "a2", "label": "Go outside", "type": "outcome"},
    ]
    edges = [
        {"from": "q1", "to": "a1", "label": "Yes"},
        {"from": "q1", "to": "a2", "label": "No"},
    ]
    elements = create_decision_tree_elements(nodes, edges)
    assert len(elements) > 0

    # Decision nodes should be diamonds, outcomes should be rectangles
    diamonds = [e for e in elements if e["type"] == "diamond"]
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(diamonds) >= 1
    assert len(rects) >= 2


def test_decision_tree_deep():
    """Multi-level decision tree."""
    nodes = [
        {"id": "q1", "label": "Budget > $100?", "type": "decision"},
        {"id": "q2", "label": "Need speed?", "type": "decision"},
        {"id": "q3", "label": "Need storage?", "type": "decision"},
        {"id": "a1", "label": "Buy SSD", "type": "outcome"},
        {"id": "a2", "label": "Buy RAM", "type": "outcome"},
        {"id": "a3", "label": "Save money", "type": "outcome"},
    ]
    edges = [
        {"from": "q1", "to": "q2", "label": "Yes"},
        {"from": "q1", "to": "q3", "label": "No"},
        {"from": "q2", "to": "a1", "label": "Yes"},
        {"from": "q2", "to": "a2", "label": "No"},
        {"from": "q3", "to": "a3", "label": "No"},
    ]
    elements = create_decision_tree_elements(nodes, edges)
    assert len(elements) > 0

    texts = [e for e in elements if e["type"] == "text"]
    assert len(texts) >= 6  # at least one text per node


def test_decision_tree_save(tmp_path):
    """Decision tree saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    nodes = [
        {"id": "q1", "label": "Continue?", "type": "decision"},
        {"id": "a1", "label": "Done", "type": "outcome"},
    ]
    edges = [{"from": "q1", "to": "a1", "label": "Yes"}]
    elements = create_decision_tree_elements(nodes, edges, title="Flow")
    path = str(tmp_path / "decision.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
