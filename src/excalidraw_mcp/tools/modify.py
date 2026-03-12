def register_modify_tools(mcp):
    @mcp.tool()
    def modify_diagram(
        file_path: str,
        add_nodes: list[dict] | None = None,
        remove_labels: list[str] | None = None,
        add_connections: list[dict] | None = None,
        output_path: str | None = None,
    ) -> str:
        """Modify an existing .excalidraw diagram.

        Args:
            file_path: Path to existing .excalidraw file
            add_nodes: Nodes to add: [{"label": "New Node", "color": "green", "x": 100, "y": 100}]
            remove_labels: Labels of nodes to remove
            add_connections: New connections: [{"from": "Node A", "to": "Node B"}]
            output_path: Optional output path (default: overwrite input file)

        Returns:
            Path to the modified file
        """
        from excalidraw_mcp.utils.file_io import load_excalidraw, save_excalidraw
        from excalidraw_mcp.elements.text import create_labeled_shape
        from excalidraw_mcp.elements.arrows import create_arrow
        from excalidraw_mcp.elements.style import get_color

        if add_nodes is None:
            add_nodes = []
        if remove_labels is None:
            remove_labels = []
        if add_connections is None:
            add_connections = []

        try:
            data = load_excalidraw(file_path)
        except (FileNotFoundError, Exception) as e:
            return f"Error reading file: {e}"
        elements = data.get("elements", [])

        # Build maps
        text_map = {}  # containerId -> text
        for el in elements:
            if el["type"] == "text" and el.get("containerId"):
                text_map[el["containerId"]] = el["text"]

        shape_map = {}  # label -> shape
        for el in elements:
            if el["type"] in ("rectangle", "ellipse", "diamond"):
                label = text_map.get(el["id"], "")
                shape_map[label] = el

        # Remove nodes
        remove_ids = set()
        for label in remove_labels:
            shape = shape_map.get(label)
            if shape:
                remove_ids.add(shape["id"])
                # Remove associated text
                for el in elements:
                    if el.get("containerId") == shape["id"]:
                        remove_ids.add(el["id"])
                # Remove associated arrows
                for el in elements:
                    if el["type"] == "arrow":
                        sb = el.get("startBinding", {})
                        eb = el.get("endBinding", {})
                        if sb.get("elementId") == shape["id"] or eb.get("elementId") == shape["id"]:
                            remove_ids.add(el["id"])

        elements = [el for el in elements if el["id"] not in remove_ids]

        # Add nodes
        for node in add_nodes:
            color = get_color(node.get("color", "blue"))
            shape, text = create_labeled_shape(
                "rectangle", id=None,
                label=node["label"],
                x=node.get("x", 100), y=node.get("y", 100),
                background_color=color["bg"],
                stroke_color=color["stroke"],
            )
            elements.extend([shape, text])
            shape_map[node["label"]] = shape

        # Add connections
        for conn in add_connections:
            start = shape_map.get(conn.get("from"))
            end = shape_map.get(conn.get("to"))
            if start and end:
                result = create_arrow(None, start, end)
                elements.extend(result)

        path = output_path or file_path
        result = save_excalidraw(elements, path)
        return f"Diagram modified and saved to: {result}"
