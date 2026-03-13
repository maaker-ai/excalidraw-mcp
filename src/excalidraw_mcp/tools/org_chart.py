"""Org chart tool — generates top-down hierarchical org charts."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width, create_centered_title
from ..elements.arrows import create_arrow
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
LEVEL_GAP = 100       # vertical gap between levels
SIBLING_GAP = 30      # horizontal gap between siblings
NODE_WIDTH = 160
NODE_HEIGHT = 50


def create_org_elements(
    root: dict,
    title: Optional[str] = None,
) -> list[dict]:
    """Create org chart elements from a tree structure.

    Args:
        root: Tree dict with 'label', optional 'children', 'color', 'description'
        title: Optional chart title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    shape_map = {}

    _calc_subtree_width(root)
    _layout_org_node(root, x=0, y=0, level=0, elements=elements, shape_map=shape_map)

    # Normalize positions
    if elements:
        all_x = [e.get("x", 0) for e in elements if "x" in e]
        min_x = min(all_x) if all_x else 0
        for e in elements:
            if "x" in e:
                e["x"] -= min_x

    if title:
        elements.insert(0, create_centered_title(title, elements))

    return elements


def _calc_subtree_width(node: dict) -> float:
    """Calculate horizontal space needed. Stores result in node['_width']."""
    children = node.get("children", [])
    if not children:
        node["_width"] = NODE_WIDTH
        return NODE_WIDTH

    total = sum(_calc_subtree_width(c) for c in children) + SIBLING_GAP * (len(children) - 1)
    node["_width"] = max(total, NODE_WIDTH)
    return node["_width"]


def _layout_org_node(
    node: dict, x: float, y: float, level: int,
    elements: list, shape_map: dict,
):
    """Recursively layout org chart nodes top-down."""
    label = node["label"]
    color_name = node.get("color", "blue" if level == 0 else "gray")
    color = get_color(color_name)

    # Create node
    display_label = label
    desc = node.get("description")
    if desc:
        display_label = f"{label}\n{desc}"

    # Center this node above its subtree
    node_x = x + node["_width"] / 2 - NODE_WIDTH / 2

    shape, text = create_labeled_shape(
        "rectangle",
        id=gen_id(),
        label=display_label,
        x=node_x, y=y,
        width=NODE_WIDTH, height=NODE_HEIGHT,
        background_color=color["bg"],
        stroke_color=color["stroke"],
        font_size=14,
    )
    shape["roundness"] = {"type": 3}
    elements.extend([shape, text])
    shape_map[label] = shape

    # Layout children
    children = node.get("children", [])
    if children:
        child_y = y + NODE_HEIGHT + LEVEL_GAP
        child_x = x

        for child in children:
            _layout_org_node(child, child_x, child_y, level + 1, elements, shape_map)

            # Connect parent to child
            child_shape = shape_map.get(child["label"])
            if child_shape:
                arrow_elems = create_arrow(
                    gen_id(), shape, child_shape,
                    strokeWidth=1,
                    endArrowhead=None,
                )
                elements.extend(arrow_elems)

            child_x += child.get("_width", NODE_WIDTH) + SIBLING_GAP


class OrgNode(BaseModel):
    label: str = Field(description="Person/role name")
    description: Optional[str] = Field(default=None, description="Title or description")
    color: Optional[str] = Field(default=None, description="Color name")
    children: Optional[list["OrgNode"]] = Field(default=None, description="Reports/subordinates")


def register_org_chart_tools(mcp: FastMCP):
    @mcp.tool()
    def create_org_chart(
        root: OrgNode,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create an organizational chart.

        Generates a top-down hierarchical org chart from a tree structure.
        Each node can have a title/description and subordinates.

        Args:
            root: Root node with label and optional children
            title: Optional chart title
            output_path: Optional output file path
            theme: Color theme

        Returns:
            Absolute path to the generated .excalidraw file
        """
        def to_dict(node: OrgNode) -> dict:
            d = {"label": node.label}
            if node.description:
                d["description"] = node.description
            if node.color:
                d["color"] = node.color
            if node.children:
                d["children"] = [to_dict(c) for c in node.children]
            return d

        root_dict = to_dict(root)
        elements = create_org_elements(root_dict, title=title)

        path = output_path or "/tmp/org-chart.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Org chart saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
