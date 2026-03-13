"""Network topology diagram tool."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width, create_centered_title
from ..elements.arrows import create_arrow
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
NODE_GAP = 250
NODE_WIDTH = 160
NODE_HEIGHT = 60

# Node type -> (shape, default_color)
NODE_TYPES = {
    "server": ("rectangle", "blue"),
    "database": ("rectangle", "green"),
    "client": ("ellipse", "gray"),
    "loadbalancer": ("diamond", "orange"),
    "firewall": ("rectangle", "red"),
    "cloud": ("ellipse", "purple"),
    "router": ("diamond", "yellow"),
    "default": ("rectangle", "blue"),
}


def create_network_elements(
    nodes: list[dict],
    links: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create network topology elements.

    Args:
        nodes: List of node dicts with 'label', optional 'type' and 'color'
        links: List of link dicts with 'from', 'to', optional 'label', 'style'
        title: Optional diagram title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    node_shapes = {}

    # Layout nodes in a grid
    cols = max(3, int(len(nodes) ** 0.5) + 1)
    for idx, node in enumerate(nodes):
        label = node["label"]
        node_type = node.get("type", "default")
        type_info = NODE_TYPES.get(node_type, NODE_TYPES["default"])
        shape_type, default_color = type_info
        color_name = node.get("color", default_color)
        color = get_color(color_name)

        col = idx % cols
        row = idx // cols
        x = col * NODE_GAP
        y = row * (NODE_HEIGHT + 80)

        shape, text = create_labeled_shape(
            shape_type,
            id=gen_id(),
            label=label,
            x=x, y=y,
            width=NODE_WIDTH, height=NODE_HEIGHT,
            background_color=color["bg"],
            stroke_color=color["stroke"],
            font_size=14,
        )
        elements.extend([shape, text])
        node_shapes[label] = shape

    # Links
    for link in links:
        from_name = link["from"]
        to_name = link["to"]
        label = link.get("label")
        style = link.get("style", "solid")

        from_shape = node_shapes.get(from_name)
        to_shape = node_shapes.get(to_name)
        if from_shape and to_shape:
            kwargs = {"strokeStyle": style}
            if link.get("bidirectional"):
                kwargs["startArrowhead"] = "arrow"
            result = create_arrow(
                gen_id(), from_shape, to_shape,
                label=label,
                **kwargs,
            )
            elements.extend(result)

    # Title
    if title:
        elements.insert(0, create_centered_title(title, elements))

    return elements


class NetworkNode(BaseModel):
    label: str = Field(description="Node label")
    type: str = Field(default="server", description="Node type: server, database, client, loadbalancer, firewall, cloud, router")
    color: Optional[str] = Field(default=None, description="Override color")


class NetworkLink(BaseModel):
    from_node: str = Field(alias="from", description="Source node label")
    to_node: str = Field(alias="to", description="Target node label")
    label: Optional[str] = Field(default=None, description="Link label")
    style: str = Field(default="solid", description="Line style: solid, dashed")
    bidirectional: bool = Field(default=False, description="Double-headed arrow")

    model_config = {"populate_by_name": True}


def register_network_tools(mcp: FastMCP):
    @mcp.tool()
    def create_network_diagram(
        nodes: list[NetworkNode],
        links: list[NetworkLink] | None = None,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a network topology diagram.

        Generates a network diagram with typed nodes (server, database,
        loadbalancer, etc.) and connections. Different node types get
        distinct shapes and colors.

        Args:
            nodes: List of network nodes with type
            links: List of connections between nodes
            title: Optional diagram title
            output_path: Optional output file path
            theme: Color theme - "light" or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        node_dicts = [
            {"label": n.label, "type": n.type, "color": n.color}
            for n in nodes
        ]

        link_dicts = []
        if links:
            for l in links:
                link_dicts.append({
                    "from": l.from_node, "to": l.to_node,
                    "label": l.label, "style": l.style,
                    "bidirectional": l.bidirectional,
                })

        elements = create_network_elements(node_dicts, link_dicts, title=title)

        path = output_path or "/tmp/network.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Network diagram saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
