"""Tests for network topology diagram tool."""

import json
import os
from excalidraw_mcp.tools.network import create_network_elements


def test_network_basic():
    """Basic network with nodes and links."""
    nodes = [
        {"label": "Server A", "type": "server"},
        {"label": "Server B", "type": "server"},
        {"label": "Database", "type": "database"},
    ]
    links = [
        {"from": "Server A", "to": "Database"},
        {"from": "Server B", "to": "Database"},
    ]
    elements = create_network_elements(nodes, links)
    assert len(elements) > 0

    # Should have arrows
    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) >= 2


def test_network_node_types():
    """Different node types get different shapes."""
    nodes = [
        {"label": "LB", "type": "loadbalancer"},
        {"label": "API", "type": "server"},
        {"label": "DB", "type": "database"},
        {"label": "User", "type": "client"},
    ]
    elements = create_network_elements(nodes, [])

    # All should have shape elements
    shapes = [e for e in elements if e["type"] in ("rectangle", "ellipse", "diamond")]
    assert len(shapes) >= 4


def test_network_with_labels():
    """Links with labels."""
    nodes = [
        {"label": "App", "type": "server"},
        {"label": "Cache", "type": "database"},
    ]
    links = [
        {"from": "App", "to": "Cache", "label": "Redis", "style": "dashed"},
    ]
    elements = create_network_elements(nodes, links)
    texts = [e for e in elements if e["type"] == "text"]
    labels = [t["text"] for t in texts]
    assert any("Redis" in l for l in labels)


def test_network_save(tmp_path):
    """Network diagram saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    nodes = [{"label": "Node1"}, {"label": "Node2"}]
    links = [{"from": "Node1", "to": "Node2"}]
    elements = create_network_elements(nodes, links, title="Network")
    path = str(tmp_path / "network.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
