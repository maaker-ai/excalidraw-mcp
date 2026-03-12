def register_export_tools(mcp):
    @mcp.tool()
    def export_diagram(file_path: str, format: str = "svg") -> str:
        """Export an .excalidraw file to SVG format.

        Args:
            file_path: Path to the .excalidraw file
            format: Export format - currently "svg" supported

        Returns:
            Path to the exported file
        """
        from excalidraw_mcp.utils.file_io import load_excalidraw
        from excalidraw_mcp.utils.svg_export import export_to_svg
        import os

        try:
            data = load_excalidraw(file_path)
        except (FileNotFoundError, Exception) as e:
            return f"Error reading file: {e}"

        if format == "svg":
            svg = export_to_svg(data)
            base, _ = os.path.splitext(file_path)
            out_path = base + ".svg"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(svg)
            return f"SVG exported to: {os.path.abspath(out_path)}"
        else:
            return f"Unsupported format: {format}. Currently only 'svg' is supported."
