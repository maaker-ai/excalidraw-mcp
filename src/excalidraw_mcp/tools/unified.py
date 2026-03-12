"""Unified diagram creation tool — routes to specific diagram tools."""

from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..utils.file_io import save_excalidraw


def route_diagram(
    diagram_type: str,
    data: dict,
    title: Optional[str] = None,
    output_path: Optional[str] = None,
    theme: str = "light",
) -> str:
    """Route to the appropriate diagram creation function.

    Args:
        diagram_type: Type of diagram to create
        data: Diagram-specific data
        title: Optional title
        output_path: Optional output path
        theme: Color theme

    Returns:
        Result message or error
    """
    dtype = diagram_type.lower().replace("-", "_").replace(" ", "_")

    if dtype == "flowchart":
        from .flowchart import FlowchartNode, FlowchartEdge
        nodes = [FlowchartNode(**n) for n in data.get("nodes", [])]
        edges = [FlowchartEdge(**{
            "from": e.get("from", e.get("from_node", "")),
            "to": e.get("to", e.get("to_node", "")),
            "label": e.get("label"),
            "style": e.get("style", "solid"),
        }) for e in data.get("edges", [])]

        from ..elements.text import create_labeled_shape, estimate_text_width
        from ..elements.arrows import create_arrow
        from ..elements.style import get_color
        from ..layout.sugiyama import sugiyama_layout

        node_data = [{"label": n.label, "shape": n.shape, "group": n.group,
                      "bg": get_color(n.color or "blue")["bg"],
                      "stroke": get_color(n.color or "blue")["stroke"]}
                     for n in nodes]
        edge_data = [{"from": e.from_node, "to": e.to_node} for e in edges]
        laid_out = sugiyama_layout(node_data, edge_data, direction=data.get("direction", "LR"))

        all_elements = []
        shape_map = {}
        for item in laid_out:
            shape, text = create_labeled_shape(
                item.get("shape", "rectangle"), id=None, label=item["label"],
                x=item["x"], y=item["y"], width=item["width"], height=item["height"],
                background_color=item["bg"], stroke_color=item.get("stroke", "#1e1e1e"),
            )
            all_elements.extend([shape, text])
            shape_map[item["label"]] = shape

        for edge in edges:
            start_el = shape_map.get(edge.from_node)
            end_el = shape_map.get(edge.to_node)
            if start_el and end_el:
                result = create_arrow(None, start_el, end_el, label=edge.label, strokeStyle=edge.style)
                all_elements.extend(result)

        if title:
            from ..elements.text import create_text
            from ..utils.ids import gen_id
            tw = estimate_text_width(title, 28)
            all_elements.insert(0, create_text(gen_id(), title, x=0, y=-50, font_size=28, width=tw))

        path = output_path or "/tmp/flowchart.excalidraw"
        result_path = save_excalidraw(all_elements, path, theme=theme)
        return f"Flowchart saved to: {result_path}"

    elif dtype == "sequence":
        from .sequence import create_sequence_elements
        participants = data.get("participants", [])
        messages = data.get("messages", [])
        elements = create_sequence_elements(participants, messages, title=title)
        path = output_path or "/tmp/sequence.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Sequence diagram saved to: {result_path}"

    elif dtype == "mindmap":
        from .mindmap import create_mindmap_elements
        root = data.get("root", data)
        elements = create_mindmap_elements(root, title=title)
        path = output_path or "/tmp/mindmap.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Mind map saved to: {result_path}"

    elif dtype in ("er", "er_diagram"):
        from .er_diagram import create_er_elements
        entities = data.get("entities", [])
        relationships = data.get("relationships", [])
        elements = create_er_elements(entities, relationships, title=title)
        path = output_path or "/tmp/er-diagram.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"ER diagram saved to: {result_path}"

    elif dtype in ("class", "class_diagram"):
        from .class_diagram import create_class_elements
        classes = data.get("classes", [])
        relationships = data.get("relationships", [])
        elements = create_class_elements(classes, relationships, title=title)
        path = output_path or "/tmp/class-diagram.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Class diagram saved to: {result_path}"

    elif dtype in ("state", "state_diagram"):
        from .state_diagram import create_state_elements
        states = data.get("states", [])
        transitions = data.get("transitions", [])
        elements = create_state_elements(states, transitions, title=title)
        path = output_path or "/tmp/state-diagram.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"State diagram saved to: {result_path}"

    elif dtype == "timeline":
        from .timeline import create_timeline_elements
        events = data.get("events", [])
        elements = create_timeline_elements(events, title=title)
        path = output_path or "/tmp/timeline.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Timeline saved to: {result_path}"

    elif dtype in ("pie", "pie_chart"):
        from .pie_chart import create_pie_elements
        slices = data.get("slices", [])
        elements = create_pie_elements(slices, title=title)
        path = output_path or "/tmp/pie-chart.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Pie chart saved to: {result_path}"

    elif dtype == "kanban":
        from .kanban import create_kanban_elements
        columns = data.get("columns", [])
        elements = create_kanban_elements(columns, title=title)
        path = output_path or "/tmp/kanban.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Kanban board saved to: {result_path}"

    elif dtype == "network":
        from .network import create_network_elements
        nodes = data.get("nodes", [])
        links = data.get("links", [])
        elements = create_network_elements(nodes, links, title=title)
        path = output_path or "/tmp/network.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Network diagram saved to: {result_path}"

    elif dtype == "quadrant":
        from .quadrant import create_quadrant_elements
        items = data.get("items", [])
        elements = create_quadrant_elements(
            items,
            x_label=data.get("x_label", "X Axis"),
            y_label=data.get("y_label", "Y Axis"),
            quadrant_labels=data.get("quadrant_labels"),
            title=title,
        )
        path = output_path or "/tmp/quadrant.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Quadrant chart saved to: {result_path}"

    elif dtype in ("journey", "user_journey"):
        from .user_journey import create_journey_elements
        steps = data.get("steps", [])
        elements = create_journey_elements(steps, title=title)
        path = output_path or "/tmp/user-journey.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"User journey saved to: {result_path}"

    elif dtype == "wireframe":
        from .wireframe import create_wireframe_elements
        components = data.get("components", [])
        device = data.get("device", "phone")
        elements = create_wireframe_elements(components, device=device, title=title)
        path = output_path or "/tmp/wireframe.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Wireframe saved to: {result_path}"

    elif dtype in ("org", "org_chart"):
        from .org_chart import create_org_elements
        root = data.get("root", data)
        elements = create_org_elements(root, title=title)
        path = output_path or "/tmp/org-chart.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Org chart saved to: {result_path}"

    elif dtype == "swot":
        from .swot import create_swot_elements
        elements = create_swot_elements(data, title=title)
        path = output_path or "/tmp/swot.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"SWOT analysis saved to: {result_path}"

    elif dtype == "architecture":
        from .architecture import register_architecture_tools
        # Use create_architecture_diagram directly would need mcp context
        # For unified routing, delegate to the elements directly
        from ..elements.text import create_labeled_shape
        from ..elements.arrows import create_arrow
        from ..elements.style import get_color
        from ..layout.grid import layered_layout

        layers = data.get("layers", [])
        connections = data.get("connections", [])
        for layer in layers:
            layer_color = layer.get("color", "blue")
            layer_c = get_color(layer_color)
            for comp in layer.get("components", []):
                comp.setdefault("bg", layer_c["bg"])
                comp.setdefault("stroke", layer_c["stroke"])

        laid_out = layered_layout(layers)
        all_elements = []
        shape_map = {}
        for item in laid_out:
            shape, text = create_labeled_shape(
                "rectangle", id=None, label=item["label"],
                x=item["x"], y=item["y"], width=item["width"], height=item["height"],
                background_color=item["bg"], stroke_color=item.get("stroke", "#1e1e1e"),
            )
            all_elements.extend([shape, text])
            shape_map[item["label"]] = shape

        for conn in connections:
            start = shape_map.get(conn.get("from"))
            end = shape_map.get(conn.get("to"))
            if start and end:
                result = create_arrow(None, start, end, label=conn.get("label"))
                all_elements.extend(result)

        path = output_path or "/tmp/architecture.excalidraw"
        result_path = save_excalidraw(all_elements, path, theme=theme)
        return f"Architecture diagram saved to: {result_path}"

    else:
        from .help import get_available_diagrams
        available = ", ".join(d["name"] for d in get_available_diagrams())
        return f"Unknown diagram type: '{diagram_type}'. Not supported.\n\nAvailable types: {available}"


def register_unified_tools(mcp: FastMCP):
    @mcp.tool()
    def create_diagram(
        diagram_type: str,
        data: dict,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create any type of diagram with a single unified tool.

        This is a convenience tool that routes to the specific diagram tool
        based on the diagram_type parameter. Use list_diagram_types to see
        all available types.

        Args:
            diagram_type: Type of diagram (flowchart, sequence, mindmap, er, class, state,
                         timeline, pie, kanban, network, quadrant, journey, wireframe, org, swot, architecture)
            data: Diagram-specific data (varies by type)
            title: Optional diagram title
            output_path: Optional output file path
            theme: Color theme - "light" or "dark"

        Returns:
            Path to generated file or error message
        """
        return route_diagram(diagram_type, data, title=title, output_path=output_path, theme=theme)
