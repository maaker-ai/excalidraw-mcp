"""Tests for module-level engine functions (decoupled from MCP)."""
import json
import os
import tempfile


def test_create_flowchart_returns_path():
    """create_flowchart should return a file path string and the file should exist."""
    from excalidraw_mcp.tools.flowchart import create_flowchart

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_flow.excalidraw")
        result = create_flowchart(
            nodes=[{"label": "A"}, {"label": "B"}],
            edges=[{"from": "A", "to": "B"}],
            output_path=path,
        )
        assert path in result
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "elements" in data


def test_create_flowchart_with_options():
    """create_flowchart should accept direction, title, theme."""
    from excalidraw_mcp.tools.flowchart import create_flowchart

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_flow2.excalidraw")
        result = create_flowchart(
            nodes=[{"label": "Start", "shape": "ellipse"}, {"label": "End", "shape": "ellipse"}],
            edges=[{"from": "Start", "to": "End"}],
            direction="TB",
            title="Test Flow",
            output_path=path,
            theme="dark",
        )
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        # Dark theme uses a dark background color
        bg = data.get("appState", {}).get("viewBackgroundColor", "")
        assert bg == "#1e1e1e"


def test_create_architecture_diagram_returns_path():
    """create_architecture_diagram should return a file path and the file should exist."""
    from excalidraw_mcp.tools.architecture import create_architecture_diagram

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_arch.excalidraw")
        result = create_architecture_diagram(
            layers=[
                {"name": "Frontend", "color": "blue", "components": [{"label": "React"}]},
                {"name": "Backend", "color": "green", "components": [{"label": "API"}]},
            ],
            connections=[{"from": "React", "to": "API"}],
            output_path=path,
        )
        assert path in result
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "elements" in data


def test_import_mermaid_flowchart_returns_path():
    """import_mermaid_flowchart should return a file path."""
    from excalidraw_mcp.tools.mermaid import import_mermaid_flowchart

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_mermaid_fc.excalidraw")
        result = import_mermaid_flowchart(
            mermaid="graph LR\n  A[Start] --> B[End]",
            output_path=path,
        )
        assert path in result
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "elements" in data


def test_import_mermaid_returns_path():
    """import_mermaid should auto-detect diagram type and return a file path."""
    from excalidraw_mcp.tools.mermaid import import_mermaid

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_mermaid.excalidraw")
        result = import_mermaid(
            mermaid="graph LR\n  A --> B",
            output_path=path,
        )
        assert path in result
        assert os.path.exists(path)


def test_import_mermaid_sequence():
    """import_mermaid should handle sequence diagrams."""
    from excalidraw_mcp.tools.mermaid import import_mermaid

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_seq.excalidraw")
        mermaid_text = "sequenceDiagram\n  Alice->>Bob: Hello\n  Bob-->>Alice: Hi"
        result = import_mermaid(mermaid=mermaid_text, output_path=path)
        assert path in result
        assert os.path.exists(path)


def test_create_sequence_diagram_returns_path():
    """create_sequence_diagram wrapper should save file and return path."""
    from excalidraw_mcp.tools.sequence import create_sequence_diagram

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_seq.excalidraw")
        result = create_sequence_diagram(
            participants=["Alice", "Bob"],
            messages=[{"from": "Alice", "to": "Bob", "label": "Hello"}],
            title="Test Sequence",
            output_path=path,
        )
        assert path in result
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "elements" in data


def test_create_mindmap_diagram_returns_path():
    """create_mindmap_diagram wrapper should save file and return path."""
    from excalidraw_mcp.tools.mindmap import create_mindmap_diagram

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_mm.excalidraw")
        result = create_mindmap_diagram(
            root={"label": "Root", "children": [{"label": "Child1"}, {"label": "Child2"}]},
            title="Test Mindmap",
            output_path=path,
        )
        assert path in result
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "elements" in data
