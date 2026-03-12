"""Test adaptive layer gap spacing."""
from excalidraw_mcp.layout.sugiyama import sugiyama_layout


def test_default_gap():
    """Default gap should be 100."""
    nodes = [{"label": "A"}, {"label": "B"}]
    edges = [{"from": "A", "to": "B"}]
    result = sugiyama_layout(nodes, edges, direction="LR")
    # Gap between nodes = B.x - (A.x + A.width)
    gap = result[1]["x"] - (result[0]["x"] + result[0]["width"])
    assert 90 <= gap <= 110  # roughly 100


def test_custom_gap():
    """Custom layer_gap should be respected."""
    nodes = [{"label": "A"}, {"label": "B"}]
    edges = [{"from": "A", "to": "B"}]
    result = sugiyama_layout(nodes, edges, direction="LR", layer_gap=200)
    gap = result[1]["x"] - (result[0]["x"] + result[0]["width"])
    assert gap > 150  # significantly larger than default


def test_small_gap():
    """Small layer_gap should produce tight layout."""
    nodes = [{"label": "A"}, {"label": "B"}]
    edges = [{"from": "A", "to": "B"}]
    result = sugiyama_layout(nodes, edges, direction="LR", layer_gap=30)
    gap = result[1]["x"] - (result[0]["x"] + result[0]["width"])
    assert gap < 80  # smaller than default
