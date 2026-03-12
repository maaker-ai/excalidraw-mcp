"""Decision tree tool — generates yes/no decision trees."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width
from ..elements.shapes import create_rectangle, create_diamond
from ..elements.lines import create_line
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
NODE_WIDTH = 160
NODE_HEIGHT = 60
H_GAP = 40
V_GAP = 80


def _build_tree(nodes_map, edges, node_id, depth=0, order=0):
    """Build layout info recursively. Returns (x, y, width) for subtree."""
    children = [(e["to"], e.get("label", "")) for e in edges if e["from"] == node_id]

    if not children:
        return {"id": node_id, "depth": depth, "order": order, "children": [], "width": NODE_WIDTH}

    child_trees = []
    for i, (child_id, label) in enumerate(children):
        ct = _build_tree(nodes_map, edges, child_id, depth + 1, i)
        ct["edge_label"] = label
        child_trees.append(ct)

    total_width = sum(c["width"] for c in child_trees) + H_GAP * (len(child_trees) - 1)
    return {"id": node_id, "depth": depth, "order": order, "children": child_trees, "width": max(total_width, NODE_WIDTH)}


def _layout_positions(tree, x_center, y_top, positions):
    """Assign (x, y) positions to each node."""
    positions[tree["id"]] = (x_center, y_top)

    if not tree["children"]:
        return

    total_width = sum(c["width"] for c in tree["children"]) + H_GAP * (len(tree["children"]) - 1)
    cx = x_center - total_width / 2

    for child in tree["children"]:
        child_center = cx + child["width"] / 2
        child_y = y_top + NODE_HEIGHT + V_GAP
        _layout_positions(child, child_center, child_y, positions)
        cx += child["width"] + H_GAP


def _collect_edges_with_labels(tree):
    """Collect (from_id, to_id, label) tuples from tree."""
    result = []
    for child in tree["children"]:
        result.append((tree["id"], child["id"], child.get("edge_label", "")))
        result.extend(_collect_edges_with_labels(child))
    return result


def create_decision_tree_elements(
    nodes: list[dict],
    edges: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create decision tree elements.

    Args:
        nodes: List of node dicts with 'id', 'label', 'type' (decision|outcome)
        edges: List of edge dicts with 'from', 'to', optional 'label'
        title: Optional chart title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []

    if not nodes:
        return elements

    nodes_map = {n["id"]: n for n in nodes}

    # Find root (node that is never a target)
    targets = {e["to"] for e in edges}
    roots = [n["id"] for n in nodes if n["id"] not in targets]
    root_id = roots[0] if roots else nodes[0]["id"]

    # Build and layout tree
    tree = _build_tree(nodes_map, edges, root_id)
    positions = {}
    _layout_positions(tree, tree["width"] / 2, 0, positions)

    # Draw nodes
    for node in nodes:
        nid = node["id"]
        if nid not in positions:
            continue
        cx, cy = positions[nid]
        x = cx - NODE_WIDTH / 2
        y = cy
        label = node["label"]
        ntype = node.get("type", "decision")

        if ntype == "decision":
            color = get_color("blue")
            shape = create_diamond(
                gen_id(), x, y, NODE_WIDTH, NODE_HEIGHT,
                background_color=color["bg"],
                stroke_color=color["stroke"],
            )
        else:
            color = get_color("green")
            shape = create_rectangle(
                gen_id(), x, y, NODE_WIDTH, NODE_HEIGHT,
                background_color=color["bg"],
                stroke_color=color["stroke"],
            )
        elements.append(shape)

        # Label text
        lw = estimate_text_width(label, 14)
        label_text = create_text(
            gen_id(), label,
            x=cx - lw / 2, y=cy + NODE_HEIGHT / 2 - 10,
            font_size=14, width=lw, height=20,
        )
        elements.append(label_text)

    # Draw edges
    edge_data = _collect_edges_with_labels(tree)
    for from_id, to_id, label in edge_data:
        if from_id not in positions or to_id not in positions:
            continue
        fx, fy = positions[from_id]
        tx, ty = positions[to_id]
        line = create_line(
            fx, fy + NODE_HEIGHT,
            tx, ty,
            stroke_color="#495057", stroke_width=2,
        )
        elements.append(line)

        # Edge label
        if label:
            mx = (fx + tx) / 2
            my = (fy + NODE_HEIGHT + ty) / 2
            lw = estimate_text_width(label, 12)
            edge_text = create_text(
                gen_id(), label,
                x=mx - lw / 2, y=my - 8,
                font_size=12, width=lw, height=16,
            )
            elements.append(edge_text)

    # Title
    if title:
        tw = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title,
            x=tree["width"] / 2 - tw / 2, y=-40,
            font_size=24, width=tw,
        )
        elements.insert(0, title_text)

    return elements


class DecisionNode(BaseModel):
    id: str = Field(description="Unique node ID")
    label: str = Field(description="Node label text")
    type: str = Field(default="decision", description="Node type: 'decision' (diamond) or 'outcome' (rectangle)")


class DecisionEdge(BaseModel):
    from_node: str = Field(alias="from", description="Source node ID")
    to_node: str = Field(alias="to", description="Target node ID")
    label: Optional[str] = Field(default=None, description="Edge label (e.g. Yes/No)")

    model_config = ConfigDict(populate_by_name=True)


def register_decision_tree_tools(mcp: FastMCP):
    @mcp.tool()
    def create_decision_tree(
        nodes: list[DecisionNode],
        edges: list[DecisionEdge],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a decision tree diagram.

        Generates a tree with diamond-shaped decision nodes and
        rectangular outcome nodes, connected by labeled edges.

        Args:
            nodes: List of nodes with id, label, and type
            edges: List of edges with from, to, and optional label
            title: Optional diagram title
            output_path: Optional output file path
            theme: Color theme

        Returns:
            Absolute path to the generated .excalidraw file
        """
        node_dicts = [{"id": n.id, "label": n.label, "type": n.type} for n in nodes]
        edge_dicts = [{"from": e.from_node, "to": e.to_node, "label": e.label} for e in edges]

        elements = create_decision_tree_elements(node_dicts, edge_dicts, title=title)

        path = output_path or "/tmp/decision-tree.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Decision tree saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
