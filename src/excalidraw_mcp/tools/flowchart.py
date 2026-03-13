from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


class FlowchartNode(BaseModel):
    label: str = Field(description="Node label text")
    color: Optional[str] = Field(default=None, description="Color name: blue, green, purple, yellow, red, gray, orange, pink")
    shape: str = Field(default="rectangle", description="Node shape: rectangle (default), diamond (for decisions), ellipse (for start/end)")
    group: Optional[str] = Field(default=None, description="Group name — nodes with same group get a background frame")
    description: Optional[str] = Field(default=None, description="Secondary text shown below the label (e.g., port, version, notes)")


class FlowchartEdge(BaseModel):
    from_node: str = Field(alias="from", description="Source node label or index (0-based)")
    to_node: str = Field(alias="to", description="Target node label or index (0-based)")
    label: Optional[str] = Field(default=None, description="Edge label")
    style: str = Field(default="solid", description="Stroke style: solid (default), dashed, dotted")
    bidirectional: bool = Field(default=False, description="If true, arrow has arrowheads on both ends")

    model_config = {"populate_by_name": True}


def register_flowchart_tools(mcp: FastMCP):
    @mcp.tool()
    def create_flowchart(
        nodes: list[FlowchartNode],
        edges: list[FlowchartEdge],
        direction: str = "LR",
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
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
            theme: Color theme - "light" (default) or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        from excalidraw_mcp.elements.text import create_labeled_shape, estimate_text_width
        from excalidraw_mcp.elements.arrows import create_arrow
        from excalidraw_mcp.elements.style import get_color
        from excalidraw_mcp.layout.sugiyama import sugiyama_layout
        from excalidraw_mcp.utils.file_io import save_excalidraw

        # 1. Prepare node data with colors, shapes, and groups
        node_data = []
        for node in nodes:
            color = get_color(node.color or "blue")
            # Combine label + description into multi-line text
            display_label = node.label
            if node.description:
                display_label = f"{node.label}\n{node.description}"
            node_data.append({
                "label": display_label,
                "_original_label": node.label,  # for edge matching
                "color": node.color or "blue",
                "shape": node.shape,
                "group": node.group,
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
        group_bounds: dict[str, list] = {}

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
            # Also index by original label (before description was appended)
            orig_label = item.get("_original_label")
            if orig_label and orig_label != item["label"]:
                shape_map[orig_label] = shape

            # Track group membership
            group_name = item.get("group")
            if group_name:
                group_bounds.setdefault(group_name, []).append(
                    {"x": item["x"], "y": item["y"], "width": item["width"], "height": item["height"]}
                )

        # 4b. Add group frames (at beginning so they render behind nodes)
        if group_bounds:
            from excalidraw_mcp.elements.groups import create_group_frame
            frame_elements = []
            for group_name, bounds in group_bounds.items():
                frame_elements.extend(create_group_frame(group_name, bounds))
            all_elements = frame_elements + all_elements

        # 5. Generate arrows
        for edge in edges:
            start_el = shape_map.get(edge.from_node)
            end_el = shape_map.get(edge.to_node)
            if start_el and end_el:
                arrow_kwargs = {"strokeStyle": edge.style}
                if edge.bidirectional:
                    arrow_kwargs["startArrowhead"] = "arrow"
                result = create_arrow(None, start_el, end_el, label=edge.label, **arrow_kwargs)
                all_elements.extend(result)

        # 6. Add title if provided
        if title:
            from excalidraw_mcp.elements.text import create_centered_title
            all_elements.insert(0, create_centered_title(title, all_elements, font_size=28))

        # 7. Save
        path = output_path or "/tmp/flowchart.excalidraw"
        result_path = save_excalidraw(all_elements, path, theme=theme)
        return f"Flowchart saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
