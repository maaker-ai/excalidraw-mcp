"""Mind map tool — generates tree-style mind maps from nested data."""

import math
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width
from ..elements.arrows import create_arrow
from ..elements.style import get_color, COLORS
from ..utils.file_io import save_excalidraw

# Layout constants
LEVEL_GAP = 250       # horizontal gap between levels
SIBLING_GAP = 30      # vertical gap between siblings
ROOT_SIZE = (220, 60) # root node dimensions
NODE_HEIGHT = 50

# Branch colors — cycle through for visual distinction
BRANCH_COLORS = ["blue", "green", "purple", "orange", "red", "pink", "yellow"]


def create_mindmap_elements(
    root: dict,
    title: Optional[str] = None,
) -> list[dict]:
    """Create mind map elements from a nested tree structure.

    Args:
        root: Tree dict with 'label' and optional 'children' (list of same structure)
        title: Optional diagram title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    shape_map = {}

    # Calculate subtree sizes for layout
    _calc_subtree_size(root)

    # Layout the tree starting from root at origin
    _layout_node(root, x=0, y=0, level=0, branch_color_idx=None,
                 elements=elements, shape_map=shape_map)

    # Normalize positions (shift so min x/y = 0)
    if elements:
        all_x = [e.get("x", 0) for e in elements]
        all_y = [e.get("y", 0) for e in elements]
        min_x = min(all_x)
        min_y = min(all_y)
        for e in elements:
            if "x" in e:
                e["x"] -= min_x
            if "y" in e:
                e["y"] -= min_y
            # Also adjust points for arrows
            if e.get("type") == "arrow" or e.get("type") == "line":
                pass  # points are relative, no adjustment needed

    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title, x=0, y=-50,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    return elements


def _calc_subtree_size(node: dict) -> float:
    """Calculate the vertical space needed for a subtree. Stores in node['_height']."""
    children = node.get("children", [])
    if not children:
        node["_height"] = NODE_HEIGHT
        return NODE_HEIGHT

    total = 0
    for child in children:
        total += _calc_subtree_size(child)
    total += SIBLING_GAP * (len(children) - 1)
    node["_height"] = max(total, NODE_HEIGHT)
    return node["_height"]


def _layout_node(
    node: dict,
    x: float,
    y: float,
    level: int,
    branch_color_idx: Optional[int],
    elements: list,
    shape_map: dict,
):
    """Recursively layout a node and its children."""
    label = node["label"]
    children = node.get("children", [])

    # Determine color
    if level == 0:
        color_name = "gray"
    elif branch_color_idx is not None:
        color_name = BRANCH_COLORS[branch_color_idx % len(BRANCH_COLORS)]
    else:
        color_name = "blue"

    color = get_color(color_name)

    # Node dimensions
    text_width = estimate_text_width(label, 18 if level == 0 else 16)
    node_width = max(text_width + 40, 160 if level == 0 else 120)
    node_height = NODE_HEIGHT

    # Create node
    shape_type = "ellipse" if level == 0 else "rectangle"
    shape, text = create_labeled_shape(
        shape_type,
        id=gen_id(),
        label=label,
        x=x, y=y,
        width=node_width, height=node_height,
        background_color=color["bg"],
        stroke_color=color["stroke"],
        font_size=18 if level == 0 else 16,
    )
    elements.extend([shape, text])
    shape_map[label] = shape

    # Layout children
    if children:
        child_x = x + node_width + LEVEL_GAP - node_width  # adjust for level gap from center
        child_x = x + LEVEL_GAP

        # Calculate total height of all children
        total_height = sum(c["_height"] for c in children) + SIBLING_GAP * (len(children) - 1)

        # Start y centered on parent
        start_y = y + node_height / 2 - total_height / 2

        current_y = start_y
        for i, child in enumerate(children):
            child_center_y = current_y + child["_height"] / 2 - NODE_HEIGHT / 2

            # Assign branch color at level 1
            if level == 0:
                child_branch_idx = i
            else:
                child_branch_idx = branch_color_idx

            _layout_node(
                child, child_x, child_center_y, level + 1,
                child_branch_idx, elements, shape_map,
            )

            # Connect parent to child
            child_shape = shape_map.get(child["label"])
            if child_shape:
                conn = create_arrow(
                    gen_id(), shape, child_shape,
                    strokeWidth=1,
                    endArrowhead=None,  # mind maps typically use lines, not arrows
                )
                elements.extend(conn)

            current_y += child["_height"] + SIBLING_GAP


class MindmapNode(BaseModel):
    label: str = Field(description="Node label text")
    children: Optional[list["MindmapNode"]] = Field(default=None, description="Child nodes")


def register_mindmap_tools(mcp: FastMCP):
    @mcp.tool()
    def create_mindmap(
        root: MindmapNode,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """Create a mind map diagram from a tree structure.

        Generates a tree-style mind map with the root node in the center-left
        and branches spreading to the right. Each top-level branch gets a
        distinct color.

        Args:
            root: Root node with label and optional children (nested tree)
            title: Optional diagram title
            output_path: Optional output file path (default: /tmp/mindmap.excalidraw)

        Returns:
            Absolute path to the generated .excalidraw file
        """
        def to_dict(node: MindmapNode) -> dict:
            d = {"label": node.label}
            if node.children:
                d["children"] = [to_dict(c) for c in node.children]
            return d

        root_dict = to_dict(root)
        elements = create_mindmap_elements(root_dict, title=title)

        path = output_path or "/tmp/mindmap.excalidraw"
        result_path = save_excalidraw(elements, path)
        return f"Mind map saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
