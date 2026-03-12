def register_architecture_tools(mcp):
    @mcp.tool()
    def create_architecture_diagram(
        layers: list[dict],
        connections: list[dict] | None = None,
        output_path: str | None = None,
    ) -> str:
        """Create a layered architecture diagram.

        Args:
            layers: List of layers, each with 'name' and 'components' list.
                    Example: [{"name": "Frontend", "color": "blue", "components": [{"label": "React App"}, {"label": "Next.js"}]}]
            connections: List of connections between components.
                    Example: [{"from": "React App", "to": "API Server"}]
            output_path: Optional output file path

        Returns:
            Path to the generated .excalidraw file
        """
        from excalidraw_mcp.elements.text import create_labeled_shape
        from excalidraw_mcp.elements.arrows import create_arrow
        from excalidraw_mcp.elements.style import get_color
        from excalidraw_mcp.layout.grid import layered_layout
        from excalidraw_mcp.utils.file_io import save_excalidraw

        if connections is None:
            connections = []

        # Apply layer colors to components (work on copies to avoid mutating input)
        # Components can have their own color (e.g., "redis", "postgres") that overrides layer color
        for layer in layers:
            layer_color = layer.get("color", "blue")
            layer_c = get_color(layer_color)
            new_comps = []
            for comp in layer.get("components", []):
                c = dict(comp)
                # Component-specific color takes priority over layer color
                comp_color_name = c.pop("color", None)
                if comp_color_name:
                    comp_c = get_color(comp_color_name)
                    c.setdefault("bg", comp_c["bg"])
                    c.setdefault("stroke", comp_c["stroke"])
                else:
                    c.setdefault("bg", layer_c["bg"])
                    c.setdefault("stroke", layer_c["stroke"])
                new_comps.append(c)
            layer["components"] = new_comps

        # Layout
        laid_out = layered_layout(layers)

        # Generate elements
        all_elements = []
        shape_map = {}

        for item in laid_out:
            shape, text = create_labeled_shape(
                "rectangle", id=None,
                label=item["label"],
                x=item["x"], y=item["y"],
                width=item["width"], height=item["height"],
                background_color=item["bg"],
                stroke_color=item.get("stroke", "#1e1e1e"),
            )
            all_elements.extend([shape, text])
            shape_map[item["label"]] = shape

        # Arrows (with optional label and style)
        for conn in connections:
            start = shape_map.get(conn.get("from"))
            end = shape_map.get(conn.get("to"))
            if start and end:
                result = create_arrow(
                    None, start, end,
                    label=conn.get("label"),
                    strokeStyle=conn.get("style", "solid"),
                )
                all_elements.extend(result)

        path = output_path or "/tmp/architecture.excalidraw"
        result_path = save_excalidraw(all_elements, path)
        return f"Architecture diagram saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
