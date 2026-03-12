"""Mermaid flowchart parser and converter.

Parses basic Mermaid flowchart syntax and converts to Excalidraw elements
via the existing flowchart tool.
"""

import re
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.file_io import save_excalidraw


def parse_mermaid_flowchart(mermaid_text: str) -> tuple[list[dict], list[dict]]:
    """Parse Mermaid flowchart syntax into nodes and edges.

    Supported syntax:
        graph LR/TD/TB/BT/RL
        A --> B                  (arrow)
        A[Label] --> B[Label]    (labeled nodes)
        A{Decision} --> B        (diamond shape)
        A([Stadium]) --> B       (ellipse shape)
        A((Circle)) --> B        (ellipse shape)
        A -->|label| B           (edge label)
        A -- label --> B         (edge label alt syntax)
        A -.-> B                 (dashed arrow)
        A ==> B                  (thick arrow, treated as solid)
        subgraph Name ... end    (grouping)

    Returns:
        (nodes, edges) where nodes have label, shape, group
        and edges have from, to, label, style
    """
    lines = mermaid_text.strip().split("\n")

    # Node registry: id -> {label, shape, group}
    node_registry: dict[str, dict] = {}
    edges: list[dict] = []
    current_group: Optional[str] = None

    for line in lines:
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("%%"):
            continue

        # Graph declaration
        if stripped.startswith("graph ") or stripped.startswith("flowchart "):
            continue

        # Subgraph start
        subgraph_match = re.match(r"subgraph\s+(.+?)(?:\s*\[.*\])?\s*$", stripped)
        if subgraph_match:
            current_group = subgraph_match.group(1).strip()
            continue

        # Subgraph end
        if stripped == "end":
            current_group = None
            continue

        # Parse edge definitions
        _parse_edge_line(stripped, node_registry, edges, current_group)

    # Build node list preserving insertion order
    nodes = list(node_registry.values())
    return nodes, edges


def _parse_node_ref(ref: str, node_registry: dict, current_group: Optional[str]) -> str:
    """Parse a node reference and register it. Returns the node ID."""
    ref = ref.strip()
    if not ref:
        return ""

    node_id = ref
    label = ref
    shape = "rectangle"

    # ((label)) — circle/ellipse
    m = re.match(r"^(\w+)\(\((.+?)\)\)$", ref)
    if m:
        node_id, label, shape = m.group(1), m.group(2), "ellipse"
    else:
        # ([label]) — stadium/ellipse
        m = re.match(r"^(\w+)\(\[(.+?)\]\)$", ref)
        if m:
            node_id, label, shape = m.group(1), m.group(2), "ellipse"
        else:
            # {label} — diamond
            m = re.match(r"^(\w+)\{(.+?)\}$", ref)
            if m:
                node_id, label, shape = m.group(1), m.group(2), "diamond"
            else:
                # [label] — rectangle
                m = re.match(r"^(\w+)\[(.+?)\]$", ref)
                if m:
                    node_id, label = m.group(1), m.group(2)
                else:
                    # (label) — rounded rectangle
                    m = re.match(r"^(\w+)\((.+?)\)$", ref)
                    if m:
                        node_id, label = m.group(1), m.group(2)

    # Register or update node
    if node_id not in node_registry:
        node_entry = {"id": node_id, "label": label, "shape": shape}
        if current_group:
            node_entry["group"] = current_group
        node_registry[node_id] = node_entry
    elif current_group and "group" not in node_registry[node_id]:
        node_registry[node_id]["group"] = current_group

    return node_id


def _parse_edge_line(line: str, node_registry: dict, edges: list, current_group: Optional[str]):
    """Parse a line that may contain edge definitions (possibly chained)."""

    # Pattern for arrow types:
    # -->  solid arrow
    # -.-> dashed arrow
    # ==> thick arrow (treated as solid)
    # -- text --> text-labeled arrow
    # -->|text| pipe-labeled arrow

    # Split by arrow patterns, keeping the arrows
    # We need to handle: A -->|label| B --> C
    # Strategy: find all arrows and split

    # First try: text-label syntax "A -- text --> B"
    text_label_pattern = re.compile(
        r"^(.+?)\s+--\s+(.+?)\s+-->\s+(.+?)$"
    )
    m = text_label_pattern.match(line)
    if m:
        from_ref = m.group(1).strip()
        label = m.group(2).strip()
        to_ref = m.group(3).strip()
        from_id = _parse_node_ref(from_ref, node_registry, current_group)
        to_id = _parse_node_ref(to_ref, node_registry, current_group)
        if from_id and to_id:
            edges.append({"from": from_id, "to": to_id, "label": label, "style": "solid"})
        return

    # General arrow pattern (handles chaining)
    # Arrow types: -->, -.->  , ==>, -->|label|
    arrow_pattern = re.compile(
        r"(\-\.\->|\-\->|==>)"  # arrow types
    )

    # Split keeping delimiters
    parts = arrow_pattern.split(line)
    if len(parts) < 3:
        return  # No arrows found

    # Process chain: [node, arrow, node, arrow, node, ...]
    i = 0
    while i < len(parts) - 2:
        from_part = parts[i].strip()
        arrow_type = parts[i + 1]
        to_part = parts[i + 2].strip()

        # Extract pipe label from from_part end or to_part start
        edge_label = ""
        style = "solid"

        if arrow_type == "-.->":
            style = "dashed"

        # Check for |label| after arrow (attached to to_part)
        pipe_label_match = re.match(r"^\|(.+?)\|\s*(.+)$", to_part)
        if pipe_label_match:
            edge_label = pipe_label_match.group(1)
            to_part = pipe_label_match.group(2).strip()

        # Only parse from_part as node on first iteration or if it has node syntax
        from_id = _parse_node_ref(from_part, node_registry, current_group)
        to_id = _parse_node_ref(to_part, node_registry, current_group)

        if from_id and to_id:
            edge_entry = {"from": from_id, "to": to_id, "style": style}
            if edge_label:
                edge_entry["label"] = edge_label
            edges.append(edge_entry)

        # For chaining, next iteration uses to_part as from
        parts[i + 2] = to_part  # update in case we stripped pipe label
        i += 2


def register_mermaid_tools(mcp: FastMCP):
    @mcp.tool()
    def import_mermaid_flowchart(
        mermaid: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Import a Mermaid flowchart and convert to Excalidraw.

        Parses Mermaid flowchart syntax and generates a hand-drawn
        Excalidraw diagram with Sugiyama layout.

        Supported Mermaid syntax:
        - Node shapes: [rect], {diamond}, ([stadium]), ((circle))
        - Arrows: -->, -.-> (dashed), ==> (thick)
        - Edge labels: -->|label| or -- label -->
        - Subgraphs: subgraph Name ... end
        - Chaining: A --> B --> C

        Args:
            mermaid: Mermaid flowchart text
            output_path: Optional output file path

        Returns:
            Absolute path to the generated .excalidraw file
        """
        from .flowchart import FlowchartNode, FlowchartEdge

        # Parse direction from graph declaration
        direction = "LR"
        first_line = mermaid.strip().split("\n")[0].strip()
        dir_match = re.search(r"(?:graph|flowchart)\s+(LR|RL|TD|TB|BT)", first_line)
        if dir_match:
            d = dir_match.group(1)
            direction = "TB" if d == "TD" else d

        nodes, edges = parse_mermaid_flowchart(mermaid)

        # Convert to FlowchartNode/FlowchartEdge
        fc_nodes = [
            FlowchartNode(
                label=n["label"],
                shape=n.get("shape", "rectangle"),
                group=n.get("group"),
            )
            for n in nodes
        ]

        fc_edges = []
        for e in edges:
            # Map node IDs to labels for the flowchart tool
            from_label = next((n["label"] for n in nodes if n["id"] == e["from"]), e["from"])
            to_label = next((n["label"] for n in nodes if n["id"] == e["to"]), e["to"])
            fc_edges.append(FlowchartEdge(
                **{"from": from_label, "to": to_label},
                label=e.get("label"),
                style=e.get("style", "solid"),
            ))

        # Use the flowchart tool's internals
        from ..elements.text import create_labeled_shape, estimate_text_width
        from ..elements.arrows import create_arrow
        from ..elements.style import get_color
        from ..layout.sugiyama import sugiyama_layout

        node_data = []
        for node in fc_nodes:
            color = get_color(node.color or "blue")
            node_data.append({
                "label": node.label,
                "shape": node.shape,
                "group": node.group,
                "bg": color["bg"],
                "stroke": color["stroke"],
            })

        edge_data = [{"from": e.from_node, "to": e.to_node} for e in fc_edges]
        laid_out = sugiyama_layout(node_data, edge_data, direction=direction)

        all_elements = []
        shape_map = {}
        group_bounds: dict[str, list] = {}

        for idx, item in enumerate(laid_out):
            shape_type = item.get("shape", "rectangle")
            shape, text = create_labeled_shape(
                shape_type, id=None, label=item["label"],
                x=item["x"], y=item["y"],
                width=item["width"], height=item["height"],
                background_color=item["bg"],
                stroke_color=item.get("stroke", "#1e1e1e"),
            )
            all_elements.extend([shape, text])
            shape_map[item["label"]] = shape

            group_name = item.get("group")
            if group_name:
                group_bounds.setdefault(group_name, []).append(
                    {"x": item["x"], "y": item["y"], "width": item["width"], "height": item["height"]}
                )

        if group_bounds:
            from ..elements.groups import create_group_frame
            frame_elements = []
            for group_name, bounds in group_bounds.items():
                frame_elements.extend(create_group_frame(group_name, bounds))
            all_elements = frame_elements + all_elements

        for edge in fc_edges:
            start_el = shape_map.get(edge.from_node)
            end_el = shape_map.get(edge.to_node)
            if start_el and end_el:
                result = create_arrow(None, start_el, end_el, label=edge.label, strokeStyle=edge.style)
                all_elements.extend(result)

        path = output_path or "/tmp/mermaid-import.excalidraw"
        result_path = save_excalidraw(all_elements, path)
        return f"Mermaid flowchart imported to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
