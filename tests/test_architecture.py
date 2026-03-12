"""Test architecture diagram enhancements."""
import json
import os
import tempfile

from excalidraw_mcp.utils.file_io import save_excalidraw, load_excalidraw


def test_architecture_connection_labels():
    """Architecture connections should support labels."""
    from excalidraw_mcp.elements.text import create_labeled_shape
    from excalidraw_mcp.elements.arrows import create_arrow
    from excalidraw_mcp.elements.style import get_color
    from excalidraw_mcp.layout.grid import layered_layout

    layers = [
        {"name": "Frontend", "color": "blue", "components": [{"label": "React"}]},
        {"name": "Backend", "color": "green", "components": [{"label": "API"}]},
    ]
    connections = [{"from": "React", "to": "API", "label": "REST API"}]

    # Apply colors
    for layer in layers:
        color = get_color(layer["color"])
        for comp in layer["components"]:
            comp["bg"] = color["bg"]
            comp["stroke"] = color["stroke"]

    laid_out = layered_layout(layers)
    all_elements = []
    shape_map = {}
    for item in laid_out:
        shape, text = create_labeled_shape(
            "rectangle", id=None, label=item["label"],
            x=item["x"], y=item["y"],
            width=item["width"], height=item["height"],
            background_color=item["bg"],
        )
        all_elements.extend([shape, text])
        shape_map[item["label"]] = shape

    for conn in connections:
        start = shape_map.get(conn["from"])
        end = shape_map.get(conn["to"])
        if start and end:
            result = create_arrow(None, start, end, label=conn.get("label"))
            all_elements.extend(result)

    texts = [e for e in all_elements if e["type"] == "text"]
    text_values = [t["text"] for t in texts]
    assert "REST API" in text_values


def test_architecture_component_color():
    """Individual components can have their own color."""
    from excalidraw_mcp.elements.text import create_labeled_shape
    from excalidraw_mcp.elements.style import get_color

    # Component with explicit color overrides layer color
    comp_color = get_color("redis")
    shape, text = create_labeled_shape(
        "rectangle", id=None, label="Redis Cache",
        x=0, y=0,
        background_color=comp_color["bg"],
        stroke_color=comp_color["stroke"],
    )
    assert shape["backgroundColor"] == comp_color["bg"]
    assert shape["strokeColor"] == comp_color["stroke"]


def test_architecture_dashed_connection():
    """Architecture connections should support dashed style."""
    from excalidraw_mcp.elements.text import create_labeled_shape
    from excalidraw_mcp.elements.arrows import create_arrow

    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=0, y=200, width=200, height=70)

    result = create_arrow(None, shape1, shape2, strokeStyle="dashed", label="optional")
    arrow = result[0]
    assert arrow["strokeStyle"] == "dashed"
    assert len(result) == 2  # arrow + label


def test_architecture_full_e2e():
    """End-to-end architecture diagram with labels and styles."""
    from excalidraw_mcp.elements.text import create_labeled_shape
    from excalidraw_mcp.elements.arrows import create_arrow
    from excalidraw_mcp.elements.style import get_color
    from excalidraw_mcp.layout.grid import layered_layout

    layers = [
        {"name": "Frontend", "color": "react", "components": [
            {"label": "React App"},
            {"label": "Next.js SSR"},
        ]},
        {"name": "Backend", "color": "nodejs", "components": [
            {"label": "API Server"},
            {"label": "Auth Service"},
        ]},
        {"name": "Data", "color": "postgres", "components": [
            {"label": "PostgreSQL"},
            {"label": "Redis Cache"},
        ]},
    ]

    connections = [
        {"from": "React App", "to": "API Server", "label": "HTTP"},
        {"from": "Next.js SSR", "to": "API Server", "label": "gRPC"},
        {"from": "API Server", "to": "PostgreSQL", "label": "SQL"},
        {"from": "API Server", "to": "Redis Cache", "label": "cache", "style": "dashed"},
        {"from": "Auth Service", "to": "Redis Cache", "label": "sessions"},
    ]

    for layer in layers:
        color = get_color(layer["color"])
        for comp in layer["components"]:
            comp["bg"] = color["bg"]
            comp["stroke"] = color["stroke"]

    laid_out = layered_layout(layers)
    all_elements = []
    shape_map = {}

    for item in laid_out:
        shape, text = create_labeled_shape(
            "rectangle", id=None, label=item["label"],
            x=item["x"], y=item["y"],
            width=item["width"], height=item["height"],
            background_color=item["bg"],
        )
        all_elements.extend([shape, text])
        shape_map[item["label"]] = shape

    for conn in connections:
        start = shape_map.get(conn["from"])
        end = shape_map.get(conn["to"])
        if start and end:
            result = create_arrow(
                None, start, end,
                label=conn.get("label"),
                strokeStyle=conn.get("style", "solid"),
            )
            all_elements.extend(result)

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw(all_elements, path)
        data = load_excalidraw(path)
        elements = data["elements"]

        rects = [e for e in elements if e["type"] == "rectangle"]
        arrows = [e for e in elements if e["type"] == "arrow"]
        texts = [e for e in elements if e["type"] == "text"]

        assert len(rects) == 6
        assert len(arrows) == 5
        # 6 component labels + 5 connection labels = 11
        assert len(texts) == 11
    finally:
        os.unlink(path)
