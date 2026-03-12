from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


class FlowchartNode(BaseModel):
    label: str = Field(description="Node label text")
    color: Optional[str] = Field(default=None, description="Color name: blue, green, purple, yellow, red, gray, orange, pink")
    shape: str = Field(default="rectangle", description="Node shape: rectangle (default), diamond (for decisions), ellipse (for start/end)")


class FlowchartEdge(BaseModel):
    from_node: str = Field(alias="from", description="Source node label or index (0-based)")
    to_node: str = Field(alias="to", description="Target node label or index (0-based)")
    label: Optional[str] = Field(default=None, description="Edge label")
    style: str = Field(default="solid", description="Stroke style: solid (default), dashed, dotted")

    model_config = {"populate_by_name": True}


def register_flowchart_tools(mcp: FastMCP):
    @mcp.tool()
    def create_flowchart(
        nodes: list[FlowchartNode],
        edges: list[FlowchartEdge],
        direction: str = "LR",
        title: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """Create a flowchart diagram with Sugiyama hierarchical auto-layout.

        Generates a hand-drawn style Excalidraw flowchart from nodes and edges.
        Handles branches, merges, cycles, and disconnected subgraphs.
        Supports Chinese/CJK text with accurate width estimation.

        Args:
            nodes: List of nodes with label and optional color
            edges: List of edges connecting nodes (by label or 0-based index)
            direction: Layout direction - "LR" (left to right), "RL", "TB" (top to bottom), "BT"
            title: Optional diagram title
            output_path: Optional output file path (default: /tmp/flowchart.excalidraw)

        Returns:
            Absolute path to the generated .excalidraw file
        """
        from excalidraw_mcp.elements.text import create_labeled_shape, estimate_text_width
        from excalidraw_mcp.elements.arrows import create_arrow
        from excalidraw_mcp.elements.style import get_color
        from excalidraw_mcp.layout.sugiyama import sugiyama_layout
        from excalidraw_mcp.utils.file_io import save_excalidraw

        # 1. Prepare node data with colors and shapes
        node_data = []
        for node in nodes:
            color = get_color(node.color or "blue")
            node_data.append({
                "label": node.label,
                "color": node.color or "blue",
                "shape": node.shape,
                "bg": color["bg"],
                "stroke": color["stroke"],
            })

        # 2. Build edge list for layout engine
        edge_data = []
        for edge in edges:
            edge_data.append({"from": edge.from_node, "to": edge.to_node})

        # 3. Run Sugiyama hierarchical layout
        laid_out = sugiyama_layout(node_data, edge_data, direction=direction)

        # 4. Generate elements
        all_elements = []
        shape_map = {}

        for idx, item in enumerate(laid_out):
            shape_type = item.get("shape", "rectangle")
            shape, text = create_labeled_shape(
                shape_type,
                id=None,
                label=item["label"],
                x=item["x"], y=item["y"],
                width=item["width"], height=item["height"],
                background_color=item["bg"],
                stroke_color=item.get("stroke", "#1e1e1e"),
            )
            all_elements.extend([shape, text])
            shape_map[item["label"]] = shape
            shape_map[str(idx)] = shape

        # 5. Generate arrows
        for edge in edges:
            start_el = shape_map.get(edge.from_node)
            end_el = shape_map.get(edge.to_node)
            if start_el and end_el:
                result = create_arrow(None, start_el, end_el, label=edge.label, strokeStyle=edge.style)
                all_elements.extend(result)

        # 6. Add title if provided
        if title:
            from excalidraw_mcp.elements.text import create_text
            from excalidraw_mcp.utils.ids import gen_id
            title_width = estimate_text_width(title, 28)
            title_text = create_text(
                gen_id(), title, x=0, y=-50,
                font_size=28, width=title_width,
            )
            all_elements.insert(0, title_text)

        # 7. Save
        path = output_path or "/tmp/flowchart.excalidraw"
        result_path = save_excalidraw(all_elements, path)
        return f"Flowchart saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
