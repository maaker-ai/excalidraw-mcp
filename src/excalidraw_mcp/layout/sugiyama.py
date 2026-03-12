"""Sugiyama hierarchical layout using grandalf.

Handles branches, merges, cycles, disconnected subgraphs,
and LR/RL/TB/BT directions. This is the primary layout engine
for flowcharts and architecture diagrams.
"""

from enum import Enum

from grandalf.graphs import Vertex as GVertex, Edge as GEdge, Graph as GGraph
from grandalf.layouts import SugiyamaLayout

from ..elements.text import estimate_text_width


class Direction(Enum):
    TOP_DOWN = "TB"
    BOTTOM_UP = "BT"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class _NodeView:
    """grandalf requires vertex.view with .w and .h attributes.
    After layout, grandalf writes .xy = (cx, cy) back here."""

    def __init__(self, w: float, h: float):
        self.w = w
        self.h = h


# Layout tuning defaults
SIBLING_GAP = 60.0    # horizontal gap between siblings in same layer
LAYER_GAP = 100.0     # vertical gap between layers
COMPONENT_GAP = 120.0  # gap between disconnected subgraphs
BOX_PADDING = 60       # text-to-box-edge padding
MIN_BOX_WIDTH = 200
BOX_HEIGHT = 70
FONT_SIZE = 20


def sugiyama_layout(
    nodes: list[dict],
    edges: list[dict],
    direction: str = "LR",
    sibling_gap: float = SIBLING_GAP,
    layer_gap: float = LAYER_GAP,
    box_height: int = BOX_HEIGHT,
) -> list[dict]:
    """Run Sugiyama hierarchical layout on a directed graph.

    Args:
        nodes: List of node dicts, each must have 'label'. Optional: 'width', 'color', 'bg', 'stroke'.
        edges: List of edge dicts with 'from' and 'to' keys (match node labels or 0-based indices).
        direction: Layout direction - "LR" (left-to-right), "RL", "TB" (top-down), "BT".
        sibling_gap: Gap between nodes in the same layer.
        layer_gap: Gap between layers.
        box_height: Height of each node box.

    Returns:
        List of node dicts (copies of input) with added x, y, width, height fields.
    """
    if not nodes:
        return []

    valid_dirs = {d.value for d in Direction}
    dir_upper = direction.upper()
    if dir_upper not in valid_dirs:
        raise ValueError(f"Invalid direction '{direction}'. Must be one of: {sorted(valid_dirs)}")
    dir_enum = Direction(dir_upper)
    is_horizontal = dir_enum in (Direction.LEFT_RIGHT, Direction.RIGHT_LEFT)

    # 1. Calculate node dimensions
    node_widths = []
    for node in nodes:
        if node.get("width"):
            node_widths.append(node["width"])
        else:
            tw = estimate_text_width(node.get("label", ""), FONT_SIZE)
            node_widths.append(max(tw + BOX_PADDING, MIN_BOX_WIDTH))

    # 2. Build grandalf graph
    # Use separate namespaces for label-based and index-based lookup to avoid collisions
    label_to_vertex: dict[str, GVertex] = {}
    index_to_vertex: dict[int, GVertex] = {}
    vertex_list = []
    for idx, node in enumerate(nodes):
        label = node.get("label", str(idx))
        v = GVertex(idx)  # use index as vertex data to avoid label collisions
        w, h = node_widths[idx], box_height
        if is_horizontal:
            v.view = _NodeView(h, w)
        else:
            v.view = _NodeView(w, h)
        label_to_vertex[label] = v
        index_to_vertex[idx] = v
        vertex_list.append(v)

    def _resolve_vertex(key: str) -> GVertex | None:
        """Resolve a node reference by label first, then by index."""
        if key in label_to_vertex:
            return label_to_vertex[key]
        try:
            return index_to_vertex[int(key)]
        except (ValueError, KeyError):
            return None

    g_edges = []
    for edge in edges:
        from_key = edge.get("from", "")
        to_key = edge.get("to", "")
        v_from = _resolve_vertex(from_key)
        v_to = _resolve_vertex(to_key)
        if v_from and v_to and v_from is not v_to:
            g_edges.append(GEdge(v_from, v_to))

    g = GGraph(vertex_list, g_edges)

    # 3. Layout each connected component
    # Key by vertex index (v.data) to avoid label collision
    index_centers: dict[int, tuple[float, float]] = {}
    offset = 0.0

    for component in g.C:
        roots = [v for v in component.sV if len(v.e_in()) == 0]
        if not roots:
            roots = [next(iter(component.sV))]

        # Handle cycles: detect feedback edges
        inverted = []
        try:
            component.get_scs_with_feedback(roots)
            inverted = [e for e in component.sE if getattr(e, "feedback", False)]
        except (AttributeError, KeyError, IndexError):
            pass  # grandalf cycle detection can fail on certain graph shapes

        sug = SugiyamaLayout(component)
        sug.xspace = sibling_gap
        sug.yspace = layer_gap
        sug.init_all(roots=roots, inverted_edges=inverted)
        sug.draw(3)  # 3 passes for better crossing reduction

        # Measure bounding box for stacking disconnected subgraphs
        comp_min = float("inf")
        comp_max = float("-inf")

        for v in component.sV:
            if hasattr(v.view, "xy"):
                cx, cy = v.view.xy
                half = v.view.w / 2
                comp_min = min(comp_min, cx - half)
                comp_max = max(comp_max, cx + half)
                index_centers[v.data] = (cx + offset, cy)

        if comp_min < float("inf"):
            offset += (comp_max - comp_min) + COMPONENT_GAP

    # 4. Transform coordinates based on direction and build result
    result = []
    for idx, node in enumerate(nodes):
        cx, cy = index_centers.get(idx, (0.0, 0.0))
        w, h = node_widths[idx], box_height

        # Transform from grandalf's native TD to requested direction
        screen_x, screen_y = _transform(cx, cy, dir_enum)

        node_copy = dict(node)
        node_copy["x"] = screen_x - w / 2
        node_copy["y"] = screen_y - h / 2
        node_copy["width"] = w
        node_copy["height"] = h
        result.append(node_copy)

    # 5. Normalize: shift so min x/y = 0
    if result:
        min_x = min(n["x"] for n in result)
        min_y = min(n["y"] for n in result)
        for n in result:
            n["x"] -= min_x
            n["y"] -= min_y

    return result


def _transform(cx: float, cy: float, direction: Direction) -> tuple[float, float]:
    """Transform grandalf's native top-down coordinates to the requested direction."""
    if direction == Direction.TOP_DOWN:
        return (cx, cy)
    elif direction == Direction.LEFT_RIGHT:
        return (cy, cx)       # rotate 90°
    elif direction == Direction.BOTTOM_UP:
        return (cx, -cy)
    elif direction == Direction.RIGHT_LEFT:
        return (-cy, cx)
    return (cx, cy)
