"""Test Sugiyama hierarchical layout."""
from excalidraw_mcp.layout.sugiyama import sugiyama_layout


def test_linear_chain_lr():
    """Linear A→B→C should lay out left-to-right."""
    nodes = [{"label": "A"}, {"label": "B"}, {"label": "C"}]
    edges = [{"from": "A", "to": "B"}, {"from": "B", "to": "C"}]
    result = sugiyama_layout(nodes, edges, direction="LR")

    assert len(result) == 3
    # Each node in a different column (increasing x)
    xs = [n["x"] for n in result]
    assert xs[0] < xs[1] < xs[2]
    # All roughly same y (single chain, no branches)
    ys = [n["y"] for n in result]
    assert ys[0] == ys[1] == ys[2]


def test_linear_chain_tb():
    """Linear A→B→C should lay out top-to-bottom."""
    nodes = [{"label": "A"}, {"label": "B"}, {"label": "C"}]
    edges = [{"from": "A", "to": "B"}, {"from": "B", "to": "C"}]
    result = sugiyama_layout(nodes, edges, direction="TB")

    ys = [n["y"] for n in result]
    assert ys[0] < ys[1] < ys[2]
    xs = [n["x"] for n in result]
    assert xs[0] == xs[1] == xs[2]


def test_branch_creates_two_paths():
    """A→B, A→C should create a branch with B and C at different positions."""
    nodes = [{"label": "A"}, {"label": "B"}, {"label": "C"}]
    edges = [{"from": "A", "to": "B"}, {"from": "A", "to": "C"}]
    result = sugiyama_layout(nodes, edges, direction="LR")

    a, b, c = result[0], result[1], result[2]
    # B and C should be in a later layer than A
    assert b["x"] > a["x"]
    assert c["x"] > a["x"]
    # B and C should be at different y positions (branched)
    assert b["y"] != c["y"]


def test_merge_diamond():
    """Diamond: A→B, A→C, B→D, C→D."""
    nodes = [{"label": "A"}, {"label": "B"}, {"label": "C"}, {"label": "D"}]
    edges = [
        {"from": "A", "to": "B"},
        {"from": "A", "to": "C"},
        {"from": "B", "to": "D"},
        {"from": "C", "to": "D"},
    ]
    result = sugiyama_layout(nodes, edges, direction="LR")

    a, b, c, d = result
    # A is leftmost, D is rightmost
    assert a["x"] < b["x"]
    assert a["x"] < c["x"]
    assert d["x"] > b["x"]
    assert d["x"] > c["x"]


def test_cycle_does_not_crash():
    """A→B→C→A cycle should not crash."""
    nodes = [{"label": "A"}, {"label": "B"}, {"label": "C"}]
    edges = [
        {"from": "A", "to": "B"},
        {"from": "B", "to": "C"},
        {"from": "C", "to": "A"},
    ]
    result = sugiyama_layout(nodes, edges, direction="LR")
    assert len(result) == 3
    # All nodes should have valid coordinates
    for n in result:
        assert "x" in n and "y" in n
        assert "width" in n and "height" in n


def test_disconnected_subgraphs():
    """Two disconnected components should both be laid out."""
    nodes = [
        {"label": "A"}, {"label": "B"},  # component 1
        {"label": "X"}, {"label": "Y"},  # component 2
    ]
    edges = [
        {"from": "A", "to": "B"},
        {"from": "X", "to": "Y"},
    ]
    result = sugiyama_layout(nodes, edges, direction="LR")
    assert len(result) == 4
    # All should have valid positions
    for n in result:
        assert n["x"] >= 0
        assert n["y"] >= 0


def test_empty_nodes():
    """Empty input should return empty."""
    assert sugiyama_layout([], []) == []


def test_single_node():
    """Single node, no edges."""
    result = sugiyama_layout([{"label": "Alone"}], [])
    assert len(result) == 1
    assert result[0]["x"] >= 0
    assert result[0]["y"] >= 0


def test_node_dimensions():
    """All nodes should get width and height."""
    nodes = [{"label": "你好世界"}, {"label": "Hi"}]
    edges = [{"from": "你好世界", "to": "Hi"}]
    result = sugiyama_layout(nodes, edges)

    for n in result:
        assert n["width"] >= 200  # MIN_BOX_WIDTH
        assert n["height"] == 70  # BOX_HEIGHT


def test_index_based_edges():
    """Edges can reference nodes by 0-based index."""
    nodes = [{"label": "First"}, {"label": "Second"}]
    edges = [{"from": "0", "to": "1"}]
    result = sugiyama_layout(nodes, edges, direction="LR")
    assert result[0]["x"] < result[1]["x"]


def test_coordinates_normalized():
    """Output coordinates should be normalized (min x/y = 0)."""
    nodes = [{"label": "A"}, {"label": "B"}, {"label": "C"}]
    edges = [{"from": "A", "to": "B"}, {"from": "B", "to": "C"}]
    result = sugiyama_layout(nodes, edges, direction="LR")

    min_x = min(n["x"] for n in result)
    min_y = min(n["y"] for n in result)
    assert min_x == 0
    assert min_y == 0
