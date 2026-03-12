"""Test Mermaid flowchart import."""
from excalidraw_mcp.tools.mermaid import parse_mermaid_flowchart


def test_parse_simple_chain():
    """Parse A --> B --> C."""
    nodes, edges = parse_mermaid_flowchart("graph LR\n    A --> B --> C")
    assert len(nodes) == 3
    assert len(edges) == 2
    labels = [n["label"] for n in nodes]
    assert "A" in labels
    assert "B" in labels
    assert "C" in labels


def test_parse_with_labels():
    """Parse A[Start] --> B[Process]."""
    nodes, edges = parse_mermaid_flowchart("graph LR\n    A[Start] --> B[Process]")
    labels = [n["label"] for n in nodes]
    assert "Start" in labels
    assert "Process" in labels


def test_parse_diamond_shape():
    """Parse B{Decision} as diamond shape."""
    nodes, edges = parse_mermaid_flowchart("graph TD\n    A[Start] --> B{Decision}")
    decision = next(n for n in nodes if n["label"] == "Decision")
    assert decision["shape"] == "diamond"


def test_parse_round_shape():
    """Parse A(Rounded) as rectangle (default)."""
    nodes, edges = parse_mermaid_flowchart("graph LR\n    A(Rounded) --> B[Square]")
    assert len(nodes) == 2


def test_parse_stadium_shape():
    """Parse A([Stadium]) as ellipse."""
    nodes, edges = parse_mermaid_flowchart("graph LR\n    A([Start]) --> B[Process]")
    start = next(n for n in nodes if n["label"] == "Start")
    assert start["shape"] == "ellipse"


def test_parse_circle_shape():
    """Parse A((Circle)) as ellipse."""
    nodes, edges = parse_mermaid_flowchart("graph LR\n    A((Hub)) --> B[Target]")
    hub = next(n for n in nodes if n["label"] == "Hub")
    assert hub["shape"] == "ellipse"


def test_parse_edge_label():
    """Parse edge labels: A -->|label| B."""
    nodes, edges = parse_mermaid_flowchart("graph LR\n    A -->|Yes| B")
    assert len(edges) == 1
    assert edges[0]["label"] == "Yes"


def test_parse_edge_label_text_syntax():
    """Parse edge labels: A -- text --> B."""
    nodes, edges = parse_mermaid_flowchart("graph LR\n    A -- Go --> B")
    assert len(edges) == 1
    assert edges[0]["label"] == "Go"


def test_parse_dotted_arrow():
    """Parse dotted arrows: A -.-> B."""
    nodes, edges = parse_mermaid_flowchart("graph LR\n    A -.-> B")
    assert edges[0]["style"] == "dashed"


def test_parse_direction():
    """Parse direction from graph declaration."""
    nodes, edges = parse_mermaid_flowchart("graph TD\n    A --> B")
    # Should return TB direction
    assert len(nodes) == 2


def test_parse_multiple_edges():
    """Parse multiple edge definitions."""
    mermaid = """graph LR
    A --> B
    B --> C
    A --> C"""
    nodes, edges = parse_mermaid_flowchart(mermaid)
    assert len(nodes) == 3
    assert len(edges) == 3


def test_parse_subgraph():
    """Parse subgraph for group assignment."""
    mermaid = """graph LR
    subgraph Backend
        A[API] --> B[DB]
    end
    C[Client] --> A"""
    nodes, edges = parse_mermaid_flowchart(mermaid)
    api = next(n for n in nodes if n["label"] == "API")
    db = next(n for n in nodes if n["label"] == "DB")
    assert api.get("group") == "Backend"
    assert db.get("group") == "Backend"
    client = next(n for n in nodes if n["label"] == "Client")
    assert client.get("group") is None
