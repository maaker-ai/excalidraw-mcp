def register_read_tools(mcp):
    @mcp.tool()
    def read_diagram(file_path: str) -> str:
        """Read and analyze an existing .excalidraw file.

        Returns a structured description of the diagram including:
        - List of shapes with labels and positions
        - List of connections between shapes
        - Color scheme used

        Args:
            file_path: Path to the .excalidraw file

        Returns:
            Human-readable description of the diagram structure
        """
        from excalidraw_mcp.utils.file_io import load_excalidraw

        try:
            data = load_excalidraw(file_path)
        except (FileNotFoundError, Exception) as e:
            return f"Error reading file: {e}"
        elements = data.get("elements", [])

        shapes = []
        texts = {}
        arrows = []

        for el in elements:
            if el["type"] in ("rectangle", "ellipse", "diamond"):
                shapes.append(el)
            elif el["type"] == "text" and el.get("containerId"):
                texts[el["containerId"]] = el["text"]
            elif el["type"] == "arrow":
                arrows.append(el)

        lines = [f"# Diagram Analysis ({len(shapes)} shapes, {len(arrows)} connections)\n"]

        lines.append("## Shapes")
        for s in shapes:
            label = texts.get(s["id"], "(no label)")
            lines.append(f"- **{label}** ({s['type']}) at ({s['x']}, {s['y']}) size {s['width']}x{s['height']} bg={s.get('backgroundColor', 'none')}")

        lines.append("\n## Connections")
        # Map element IDs to labels
        id_to_label = {}
        for s in shapes:
            id_to_label[s["id"]] = texts.get(s["id"], s["id"])

        for a in arrows:
            start_id = a.get("startBinding", {}).get("elementId", "?")
            end_id = a.get("endBinding", {}).get("elementId", "?")
            start_label = id_to_label.get(start_id, start_id)
            end_label = id_to_label.get(end_id, end_id)
            lines.append(f"- {start_label} → {end_label}")

        return "\n".join(lines)
