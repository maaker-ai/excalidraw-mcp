"""Help tool — lists available diagram types and capabilities."""

from mcp.server.fastmcp import FastMCP


DIAGRAM_TYPES = [
    {"name": "flowchart", "tool": "create_flowchart", "description": "Flowcharts with Sugiyama auto-layout, branches, merges, cycles"},
    {"name": "sequence", "tool": "create_sequence_diagram", "description": "UML sequence diagrams with lifelines and messages"},
    {"name": "architecture", "tool": "create_architecture_diagram", "description": "Layered architecture diagrams with connections"},
    {"name": "mindmap", "tool": "create_mindmap", "description": "Tree-style mind maps with branch colors"},
    {"name": "er_diagram", "tool": "create_er_diagram", "description": "Entity-Relationship diagrams with attributes and cardinality"},
    {"name": "class_diagram", "tool": "create_class_diagram", "description": "UML class diagrams with attributes, methods, relationships"},
    {"name": "state_diagram", "tool": "create_state_diagram", "description": "UML state machines with initial/final states and transitions"},
    {"name": "timeline", "tool": "create_timeline", "description": "Timeline/Gantt charts with overlapping event handling"},
    {"name": "pie_chart", "tool": "create_pie_chart", "description": "Pie charts with labeled slices and percentages"},
    {"name": "kanban", "tool": "create_kanban_board", "description": "Kanban boards with columns and cards"},
    {"name": "network", "tool": "create_network_diagram", "description": "Network topology with typed nodes (server, DB, etc.)"},
    {"name": "quadrant", "tool": "create_quadrant_chart", "description": "2x2 priority/positioning matrices"},
    {"name": "user_journey", "tool": "create_user_journey", "description": "User journey maps with emotion indicators"},
    {"name": "wireframe", "tool": "create_wireframe", "description": "UI wireframe mockups with device frames"},
    {"name": "org_chart", "tool": "create_org_chart", "description": "Organizational charts (top-down hierarchy)"},
    {"name": "swot", "tool": "create_swot_analysis", "description": "SWOT analysis 2x2 color-coded matrices"},
    {"name": "mermaid_import", "tool": "import_mermaid", "description": "Import Mermaid syntax (flowchart, sequence, class)"},
    {"name": "read", "tool": "read_diagram", "description": "Read and analyze existing .excalidraw files"},
    {"name": "modify", "tool": "modify_diagram", "description": "Add/remove nodes and connections to existing diagrams"},
    {"name": "export", "tool": "export_to_svg", "description": "Export diagrams to SVG format"},
]


def get_available_diagrams() -> list[dict]:
    """Return list of available diagram types with descriptions."""
    return DIAGRAM_TYPES


def register_help_tools(mcp: FastMCP):
    @mcp.tool()
    def list_diagram_types() -> str:
        """List all available diagram types and tools.

        Returns a formatted list of all diagram types this MCP server
        can generate, with tool names and descriptions.

        Returns:
            Formatted list of available diagram types
        """
        lines = ["# Available Diagram Types\n"]
        for d in DIAGRAM_TYPES:
            lines.append(f"- **{d['name']}** (`{d['tool']}`): {d['description']}")
        lines.append(f"\nTotal: {len(DIAGRAM_TYPES)} diagram types available.")
        lines.append("\nAll tools support `theme` parameter ('light' or 'dark') and custom `output_path`.")
        return "\n".join(lines)
