"""Test flowchart generation."""
import json
import os
import tempfile

from excalidraw_mcp.elements.text import create_labeled_shape, estimate_text_width
from excalidraw_mcp.elements.arrows import create_arrow
from excalidraw_mcp.elements.style import get_color
from excalidraw_mcp.layout.grid import grid_layout
from excalidraw_mcp.utils.file_io import save_excalidraw, load_excalidraw


def test_estimate_text_width_ascii():
    w = estimate_text_width("Hello", 20)
    assert 50 < w < 60  # ~55


def test_estimate_text_width_cjk():
    w = estimate_text_width("你好世界", 20)
    assert 80 < w < 100  # ~88


def test_estimate_text_width_mixed():
    w = estimate_text_width("API Server", 20)
    w_cjk = estimate_text_width("用户请求", 20)
    assert w > 0
    assert w_cjk > 0


def test_create_labeled_shape_text_centered():
    shape, text = create_labeled_shape(
        "rectangle", id="box1", label="测试文字",
        x=100, y=50, width=250, height=70,
    )
    # Text should be centered in the shape
    expected_x = 100 + (250 - text["width"]) / 2
    expected_y = 50 + (70 - text["height"]) / 2
    assert abs(text["x"] - expected_x) < 0.01
    assert abs(text["y"] - expected_y) < 0.01


def test_create_labeled_shape_auto_id():
    shape, text = create_labeled_shape(
        "rectangle", id=None, label="Auto ID",
        x=0, y=0,
    )
    assert shape["id"] is not None
    assert text["id"] == shape["id"] + "_text"
    assert text["containerId"] == shape["id"]


def test_create_labeled_shape_binding():
    shape, text = create_labeled_shape(
        "rectangle", id="s1", label="Test",
        x=0, y=0,
    )
    assert {"id": "s1_text", "type": "text"} in shape["boundElements"]
    assert text["containerId"] == "s1"


def test_arrow_fixedpoint_orbit():
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=0, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2)
    arrow = result[0]

    assert arrow["startBinding"]["mode"] == "orbit"
    assert arrow["endBinding"]["mode"] == "orbit"
    assert arrow["startBinding"]["fixedPoint"] == [1.0, 0.5001]  # right edge
    assert arrow["endBinding"]["fixedPoint"] == [0.0, 0.5001]    # left edge


def test_arrow_auto_id():
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=0, width=200, height=70)

    result = create_arrow(None, shape1, shape2)
    arrow = result[0]
    assert arrow["id"] is not None
    assert arrow["id"].startswith("arrow_")


def test_arrow_coordinates():
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=0, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2)
    arrow = result[0]

    # Arrow starts at right edge of shape1
    assert arrow["x"] == 200  # shape1.x + shape1.width
    assert arrow["y"] == 35   # shape1.y + shape1.height / 2
    # Points relative to start
    assert arrow["points"][0] == [0, 0]
    assert arrow["points"][1] == [100, 0]  # dx to left edge of shape2


def test_arrow_vertical():
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=0, y=200, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2)
    arrow = result[0]
    assert arrow["startBinding"]["fixedPoint"] == [0.5001, 1.0]  # bottom
    assert arrow["endBinding"]["fixedPoint"] == [0.5001, 0.0]    # top


def test_grid_layout_horizontal():
    nodes = [
        {"label": "A"},
        {"label": "B"},
        {"label": "C"},
    ]
    result = grid_layout(nodes, direction="horizontal", columns=3)
    assert len(result) == 3
    # All on same row
    assert result[0]["y"] == result[1]["y"] == result[2]["y"]
    # Increasing x
    assert result[0]["x"] < result[1]["x"] < result[2]["x"]


def test_grid_layout_vertical():
    nodes = [
        {"label": "A"},
        {"label": "B"},
        {"label": "C"},
    ]
    result = grid_layout(nodes, direction="vertical", columns=1)
    assert len(result) == 3
    # All in same column
    assert result[0]["x"] == result[1]["x"] == result[2]["x"]
    # Increasing y
    assert result[0]["y"] < result[1]["y"] < result[2]["y"]


def test_save_and_load():
    shape, text = create_labeled_shape("rectangle", id="s1", label="Test", x=0, y=0)
    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw([shape, text], path)
        data = load_excalidraw(path)
        assert data["type"] == "excalidraw"
        assert data["source"] == "maaker-ai/excalidraw-mcp"
        assert len(data["elements"]) == 2
    finally:
        os.unlink(path)


def test_colors():
    for name in ["blue", "green", "purple", "yellow", "red", "gray", "orange", "pink"]:
        c = get_color(name)
        assert "bg" in c
        assert "stroke" in c

    # Unknown color falls back to blue
    assert get_color("nonexistent") == get_color("blue")


def test_full_flowchart():
    """End-to-end: create a flowchart with CJK text, save, reload, verify."""
    nodes = [
        {"label": "用户请求", "bg": "#a5d8ff", "stroke": "#1971c2"},
        {"label": "负载均衡", "bg": "#b2f2bb", "stroke": "#2f9e44"},
        {"label": "API Server", "bg": "#d0bfff", "stroke": "#7048e8"},
    ]

    laid_out = grid_layout(nodes, direction="horizontal", columns=3)
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

    # Add arrows
    for f, t in [("用户请求", "负载均衡"), ("负载均衡", "API Server")]:
        result = create_arrow(None, shape_map[f], shape_map[t])
        all_elements.extend(result)

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw(all_elements, path)
        data = load_excalidraw(path)

        elements = data["elements"]
        shapes = [e for e in elements if e["type"] == "rectangle"]
        texts = [e for e in elements if e["type"] == "text"]
        arrows = [e for e in elements if e["type"] == "arrow"]

        assert len(shapes) == 3
        assert len(texts) == 3
        assert len(arrows) == 2

        # Verify text centering
        for text_el in texts:
            container = next(e for e in shapes if e["id"] == text_el["containerId"])
            expected_x = container["x"] + (container["width"] - text_el["width"]) / 2
            assert abs(text_el["x"] - expected_x) < 0.01, f"Text '{text_el['text']}' not centered"

        # Verify arrow bindings use fixedPoint + orbit
        for arrow_el in arrows:
            assert arrow_el["startBinding"]["mode"] == "orbit"
            assert arrow_el["endBinding"]["mode"] == "orbit"
            assert "fixedPoint" in arrow_el["startBinding"]
            assert "fixedPoint" in arrow_el["endBinding"]
    finally:
        os.unlink(path)


def test_arrow_with_label():
    """Arrow with label should return arrow + text element."""
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=0, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2, label="Yes")
    # Should return a list: [arrow, text]
    assert isinstance(result, list)
    assert len(result) == 2
    arrow, text = result
    assert arrow["type"] == "arrow"
    assert text["type"] == "text"
    assert text["text"] == "Yes"
    assert text["containerId"] == "arr1"
    assert {"id": text["id"], "type": "text"} in arrow["boundElements"]


def test_arrow_without_label():
    """Arrow without label should return a single-element list for consistency."""
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=0, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2)
    # Without label, should return list with just the arrow
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "arrow"


def test_arrow_label_position():
    """Arrow label should be positioned at the midpoint of the arrow."""
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=400, y=0, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2, label="条件")
    arrow, text = result

    # Text midpoint should be roughly at arrow midpoint
    arrow_mid_x = arrow["x"] + arrow["points"][1][0] / 2
    arrow_mid_y = arrow["y"] + arrow["points"][1][1] / 2
    text_mid_x = text["x"] + text["width"] / 2
    text_mid_y = text["y"] + text["height"] / 2

    assert abs(text_mid_x - arrow_mid_x) < 5
    assert abs(text_mid_y - arrow_mid_y) < 5


# ========== Iteration 2: Node shape support ==========

def test_flowchart_node_shape_field():
    """FlowchartNode should accept a shape field."""
    from excalidraw_mcp.tools.flowchart import FlowchartNode
    node = FlowchartNode(label="Decision", shape="diamond")
    assert node.shape == "diamond"

    node_default = FlowchartNode(label="Step")
    assert node_default.shape == "rectangle"


def test_flowchart_node_shape_ellipse():
    """FlowchartNode should accept ellipse shape."""
    from excalidraw_mcp.tools.flowchart import FlowchartNode
    node = FlowchartNode(label="Start", shape="ellipse")
    assert node.shape == "ellipse"


def test_flowchart_generates_diamond_shape():
    """create_flowchart with diamond shape should produce diamond elements."""
    import tempfile
    from excalidraw_mcp.tools.flowchart import FlowchartNode, FlowchartEdge
    # Simulate what create_flowchart does internally
    from excalidraw_mcp.elements.text import create_labeled_shape
    from excalidraw_mcp.elements.style import get_color

    color = get_color("yellow")
    shape, text = create_labeled_shape(
        "diamond", id="d1", label="Decision?",
        x=0, y=0,
        background_color=color["bg"], stroke_color=color["stroke"],
    )
    assert shape["type"] == "diamond"
    assert text["containerId"] == "d1"


def test_flowchart_generates_ellipse_shape():
    """create_flowchart with ellipse shape should produce ellipse elements."""
    from excalidraw_mcp.elements.text import create_labeled_shape
    from excalidraw_mcp.elements.style import get_color

    color = get_color("green")
    shape, text = create_labeled_shape(
        "ellipse", id="e1", label="Start",
        x=0, y=0,
        background_color=color["bg"], stroke_color=color["stroke"],
    )
    assert shape["type"] == "ellipse"
    assert text["containerId"] == "e1"


def test_flowchart_mixed_shapes_e2e():
    """End-to-end: flowchart with mixed shapes (rectangle, diamond, ellipse)."""
    import tempfile
    from excalidraw_mcp.elements.text import create_labeled_shape
    from excalidraw_mcp.elements.arrows import create_arrow
    from excalidraw_mcp.elements.style import get_color
    from excalidraw_mcp.layout.sugiyama import sugiyama_layout
    from excalidraw_mcp.utils.file_io import save_excalidraw, load_excalidraw

    nodes = [
        {"label": "Start", "color": "green", "shape": "ellipse"},
        {"label": "Process", "color": "blue", "shape": "rectangle"},
        {"label": "Decision?", "color": "yellow", "shape": "diamond"},
        {"label": "End", "color": "red", "shape": "ellipse"},
    ]
    edge_data = [
        {"from": "Start", "to": "Process"},
        {"from": "Process", "to": "Decision?"},
        {"from": "Decision?", "to": "End"},
    ]

    laid_out = sugiyama_layout(nodes, edge_data, direction="LR")
    all_elements = []
    shape_map = {}

    for idx, item in enumerate(laid_out):
        shape_type = nodes[idx].get("shape", "rectangle")
        color = get_color(nodes[idx]["color"])
        shape, text = create_labeled_shape(
            shape_type,
            id=None, label=item["label"],
            x=item["x"], y=item["y"],
            width=item["width"], height=item["height"],
            background_color=color["bg"], stroke_color=color["stroke"],
        )
        all_elements.extend([shape, text])
        shape_map[item["label"]] = shape

    for edge in edge_data:
        result = create_arrow(None, shape_map[edge["from"]], shape_map[edge["to"]])
        all_elements.extend(result)

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw(all_elements, path)
        data = load_excalidraw(path)
        elements = data["elements"]

        ellipses = [e for e in elements if e["type"] == "ellipse"]
        diamonds = [e for e in elements if e["type"] == "diamond"]
        rectangles = [e for e in elements if e["type"] == "rectangle"]

        assert len(ellipses) == 2, f"Expected 2 ellipses, got {len(ellipses)}"
        assert len(diamonds) == 1, f"Expected 1 diamond, got {len(diamonds)}"
        assert len(rectangles) == 1, f"Expected 1 rectangle, got {len(rectangles)}"
    finally:
        os.unlink(path)


# ========== Iteration 3: Edge stroke styles ==========

def test_edge_style_field():
    """FlowchartEdge should accept a style field."""
    from excalidraw_mcp.tools.flowchart import FlowchartEdge
    edge = FlowchartEdge(**{"from": "A", "to": "B", "style": "dashed"})
    assert edge.style == "dashed"

    edge_default = FlowchartEdge(**{"from": "A", "to": "B"})
    assert edge_default.style == "solid"


def test_arrow_dashed_style():
    """Arrow with dashed style should have strokeStyle='dashed'."""
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=0, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2, strokeStyle="dashed")
    arrow = result[0]
    assert arrow["strokeStyle"] == "dashed"


def test_arrow_dotted_style():
    """Arrow with dotted style should have strokeStyle='dotted'."""
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=0, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2, strokeStyle="dotted")
    arrow = result[0]
    assert arrow["strokeStyle"] == "dotted"


# ========== Iteration 4: Node grouping with frames ==========

def test_flowchart_node_group_field():
    """FlowchartNode should accept an optional group field."""
    from excalidraw_mcp.tools.flowchart import FlowchartNode
    node = FlowchartNode(label="API", group="Backend")
    assert node.group == "Backend"

    node_default = FlowchartNode(label="Step")
    assert node_default.group is None


def test_create_group_frame():
    """create_group_frame should produce a background rectangle with label."""
    from excalidraw_mcp.elements.groups import create_group_frame

    # Simulate some node positions
    node_bounds = [
        {"x": 0, "y": 0, "width": 200, "height": 70},
        {"x": 300, "y": 0, "width": 200, "height": 70},
    ]
    frame_elements = create_group_frame("Backend", node_bounds, color="blue")
    assert len(frame_elements) == 2  # frame rect + label text
    frame_rect = frame_elements[0]
    frame_label = frame_elements[1]

    assert frame_rect["type"] == "rectangle"
    # Frame should encompass all nodes with padding
    assert frame_rect["x"] < 0  # padding before first node
    assert frame_rect["width"] > 500  # wider than nodes span
    assert frame_label["type"] == "text"
    assert frame_label["text"] == "Backend"


def test_flowchart_with_groups_e2e():
    """End-to-end: flowchart with groups should have frame rectangles."""
    import tempfile
    from excalidraw_mcp.elements.text import create_labeled_shape
    from excalidraw_mcp.elements.arrows import create_arrow
    from excalidraw_mcp.elements.style import get_color
    from excalidraw_mcp.elements.groups import create_group_frame
    from excalidraw_mcp.layout.sugiyama import sugiyama_layout
    from excalidraw_mcp.utils.file_io import save_excalidraw, load_excalidraw

    nodes = [
        {"label": "React", "color": "blue", "group": "Frontend"},
        {"label": "Next.js", "color": "blue", "group": "Frontend"},
        {"label": "API", "color": "green", "group": "Backend"},
        {"label": "DB", "color": "purple", "group": "Backend"},
    ]
    edge_data = [
        {"from": "React", "to": "API"},
        {"from": "Next.js", "to": "API"},
        {"from": "API", "to": "DB"},
    ]

    laid_out = sugiyama_layout(nodes, edge_data, direction="LR")
    all_elements = []
    shape_map = {}
    group_bounds: dict[str, list] = {}

    for idx, item in enumerate(laid_out):
        color = get_color(nodes[idx]["color"])
        shape, text = create_labeled_shape(
            "rectangle", id=None, label=item["label"],
            x=item["x"], y=item["y"],
            width=item["width"], height=item["height"],
            background_color=color["bg"], stroke_color=color["stroke"],
        )
        all_elements.extend([shape, text])
        shape_map[item["label"]] = shape

        group_name = nodes[idx].get("group")
        if group_name:
            group_bounds.setdefault(group_name, []).append(
                {"x": item["x"], "y": item["y"], "width": item["width"], "height": item["height"]}
            )

    # Add group frames (at the beginning so they render behind nodes)
    for group_name, bounds in group_bounds.items():
        frame_elements = create_group_frame(group_name, bounds)
        all_elements = frame_elements + all_elements

    for edge in edge_data:
        result = create_arrow(None, shape_map[edge["from"]], shape_map[edge["to"]])
        all_elements.extend(result)

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw(all_elements, path)
        data = load_excalidraw(path)
        elements = data["elements"]

        # Should have 4 node rects + 2 frame rects = 6 rectangles
        rects = [e for e in elements if e["type"] == "rectangle"]
        assert len(rects) == 6, f"Expected 6 rectangles (4 nodes + 2 frames), got {len(rects)}"

        # Should have group label texts
        texts = [e for e in elements if e["type"] == "text"]
        text_values = [t["text"] for t in texts]
        assert "Frontend" in text_values
        assert "Backend" in text_values
    finally:
        os.unlink(path)
