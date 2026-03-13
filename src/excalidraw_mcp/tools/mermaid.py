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


def parse_mermaid_sequence(mermaid_text: str) -> tuple[list[str], list[dict]]:
    """Parse Mermaid sequence diagram syntax.

    Supported:
        sequenceDiagram
        participant A as Alice
        Alice->>Bob: message      (solid arrow)
        Bob-->>Alice: response    (dashed return arrow)
        Alice->>Alice: self       (self-message)

    Returns:
        (participants, messages) where participants is a list of display names
        and messages have from, to, label, style
    """
    lines = mermaid_text.strip().split("\n")
    aliases: dict[str, str] = {}  # short -> display name
    participants_ordered: list[str] = []
    messages: list[dict] = []

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped == "sequenceDiagram" or stripped.startswith("%%"):
            continue

        # participant A as Alice
        m = re.match(r"participant\s+(\S+)\s+as\s+(.+)$", stripped)
        if m:
            short, display = m.group(1), m.group(2).strip()
            aliases[short] = display
            if display not in participants_ordered:
                participants_ordered.append(display)
            continue

        # participant Alice (no alias)
        m = re.match(r"participant\s+(\S+)\s*$", stripped)
        if m:
            name = m.group(1)
            if name not in participants_ordered:
                participants_ordered.append(name)
            continue

        # Message patterns:
        # A->>B: text       (solid)
        # A-->>B: text      (dashed)
        # A-)B: text        (async, treat as solid)
        # A--)B: text       (async dashed)
        m = re.match(r"(\S+?)\s*(-->>|->>|--\)|->)\s*(\S+?)\s*:\s*(.*)$", stripped)
        if m:
            from_id = m.group(1)
            arrow = m.group(2)
            to_id = m.group(3)
            label = m.group(4).strip()

            # Resolve aliases
            from_name = aliases.get(from_id, from_id)
            to_name = aliases.get(to_id, to_id)

            # Auto-register participants
            if from_name not in participants_ordered:
                participants_ordered.append(from_name)
            if to_name not in participants_ordered:
                participants_ordered.append(to_name)

            style = "dashed" if arrow.startswith("--") else "solid"
            messages.append({
                "from": from_name,
                "to": to_name,
                "label": label,
                "style": style,
            })

    return participants_ordered, messages


def parse_mermaid_class(mermaid_text: str) -> tuple[list[dict], list[dict]]:
    """Parse Mermaid class diagram syntax.

    Supported:
        classDiagram
        class ClassName {
            +String attr
            -int id
            +method()
            -privateMethod()
        }
        Animal <|-- Dog         (inheritance)
        Customer --> Order      (association)
        Order *-- LineItem      (composition)
        Order o-- Product       (aggregation)
        A -- B : label          (with label)

    Returns:
        (classes, relationships) where classes have name, attributes, methods
    """
    lines = mermaid_text.strip().split("\n")

    class_registry: dict[str, dict] = {}
    relationships: list[dict] = []
    current_class: Optional[str] = None
    in_class_body = False

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped == "classDiagram" or stripped.startswith("%%"):
            continue

        # Class body end
        if stripped == "}":
            current_class = None
            in_class_body = False
            continue

        # Class definition start: class Name {
        m = re.match(r"class\s+(\w+)\s*\{?\s*$", stripped)
        if m:
            class_name = m.group(1)
            if class_name not in class_registry:
                class_registry[class_name] = {"name": class_name, "attributes": [], "methods": []}
            if "{" in stripped:
                current_class = class_name
                in_class_body = True
            continue

        # Inside class body — attributes and methods
        if in_class_body and current_class:
            # Method has ()
            if "(" in stripped and ")" in stripped:
                class_registry[current_class]["methods"].append(stripped)
            else:
                class_registry[current_class]["attributes"].append(stripped)
            continue

        # Relationship patterns
        # A <|-- B (inheritance: B inherits A)
        m = re.match(r'(\w+)\s+<\|--\s+(\w+)(?:\s*:\s*(.+))?', stripped)
        if m:
            _ensure_class(class_registry, m.group(1))
            _ensure_class(class_registry, m.group(2))
            relationships.append({
                "from": m.group(2), "to": m.group(1),
                "type": "inheritance", "label": (m.group(3) or "").strip(),
            })
            continue

        # A *-- B (composition)
        m = re.match(r'(\w+)\s+\*--\s+(\w+)(?:\s*:\s*(.+))?', stripped)
        if m:
            _ensure_class(class_registry, m.group(1))
            _ensure_class(class_registry, m.group(2))
            relationships.append({
                "from": m.group(1), "to": m.group(2),
                "type": "composition", "label": (m.group(3) or "").strip(),
            })
            continue

        # A o-- B (aggregation)
        m = re.match(r'(\w+)\s+o--\s+(\w+)(?:\s*:\s*(.+))?', stripped)
        if m:
            _ensure_class(class_registry, m.group(1))
            _ensure_class(class_registry, m.group(2))
            relationships.append({
                "from": m.group(1), "to": m.group(2),
                "type": "aggregation", "label": (m.group(3) or "").strip(),
            })
            continue

        # A "card1" --> "card2" B : label (with cardinality)
        m = re.match(r'(\w+)\s+"[^"]*"\s*-->\s*"[^"]*"\s*(\w+)(?:\s*:\s*(.+))?', stripped)
        if m:
            _ensure_class(class_registry, m.group(1))
            _ensure_class(class_registry, m.group(2))
            relationships.append({
                "from": m.group(1), "to": m.group(2),
                "type": "association", "label": (m.group(3) or "").strip(),
            })
            continue

        # A --> B (association)
        m = re.match(r'(\w+)\s+-->\s+(\w+)(?:\s*:\s*(.+))?', stripped)
        if m:
            _ensure_class(class_registry, m.group(1))
            _ensure_class(class_registry, m.group(2))
            relationships.append({
                "from": m.group(1), "to": m.group(2),
                "type": "association", "label": (m.group(3) or "").strip(),
            })
            continue

        # A -- B (plain link)
        m = re.match(r'(\w+)\s+--\s+(\w+)(?:\s*:\s*(.+))?', stripped)
        if m:
            _ensure_class(class_registry, m.group(1))
            _ensure_class(class_registry, m.group(2))
            relationships.append({
                "from": m.group(1), "to": m.group(2),
                "type": "association", "label": (m.group(3) or "").strip(),
            })
            continue

    return list(class_registry.values()), relationships


def parse_mermaid_state(mermaid_text: str) -> tuple[list[dict], list[dict]]:
    """Parse Mermaid state diagram syntax.

    Supported:
        stateDiagram-v2
        [*] --> StateA          (initial transition)
        StateA --> StateB : event
        StateB --> [*]          (final transition)

    Returns:
        (states, transitions) where states have name, is_initial, is_final
    """
    lines = mermaid_text.strip().split("\n")

    state_registry: dict[str, dict] = {}
    transitions: list[dict] = []
    initial_targets: set[str] = set()
    final_sources: set[str] = set()

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped.startswith("stateDiagram") or stripped.startswith("%%"):
            continue

        # Transition: A --> B : label
        m = re.match(r'(\[\*\]|\w+)\s*-->\s*(\[\*\]|\w+)(?:\s*:\s*(.+))?', stripped)
        if m:
            from_name = m.group(1).strip()
            to_name = m.group(2).strip()
            label = (m.group(3) or "").strip()

            # Handle [*] for initial/final
            if from_name == "[*]":
                initial_targets.add(to_name)
                _ensure_state(state_registry, to_name)
                transitions.append({"from": to_name, "to": to_name, "label": label})
                continue
            elif to_name == "[*]":
                final_sources.add(from_name)
                _ensure_state(state_registry, from_name)
                continue

            _ensure_state(state_registry, from_name)
            _ensure_state(state_registry, to_name)
            transitions.append({"from": from_name, "to": to_name, "label": label})

    # Mark initial/final states
    for name in initial_targets:
        if name in state_registry:
            state_registry[name]["is_initial"] = True
    for name in final_sources:
        if name in state_registry:
            state_registry[name]["is_final"] = True

    # Filter out self-loops from [*] handling
    transitions = [t for t in transitions if not (t["from"] == t["to"] and not t["label"])]

    return list(state_registry.values()), transitions


def parse_mermaid_pie(mermaid_text: str) -> tuple[list[dict], Optional[str]]:
    """Parse Mermaid pie chart syntax.

    Supported:
        pie title My Title
        "Label" : value
        "Label2" : value2

    Returns:
        (slices, title) where slices have label and value
    """
    lines = mermaid_text.strip().split("\n")
    slices = []
    title = None

    for line in lines:
        stripped = line.strip()

        if not stripped or stripped.startswith("%%"):
            continue

        # pie title ...
        m = re.match(r"^pie\s+title\s+(.+)$", stripped)
        if m:
            title = m.group(1).strip()
            continue

        # Just "pie"
        if stripped == "pie":
            continue

        # "Label" : value
        m = re.match(r'^"(.+?)"\s*:\s*([\d.]+)', stripped)
        if m:
            slices.append({"label": m.group(1), "value": float(m.group(2))})

    return slices, title


def _ensure_state(registry: dict, name: str):
    """Ensure a state exists in the registry."""
    if name not in registry:
        registry[name] = {"name": name, "is_initial": False, "is_final": False}


def _ensure_class(registry: dict, name: str):
    """Ensure a class exists in the registry."""
    if name not in registry:
        registry[name] = {"name": name, "attributes": [], "methods": []}


def import_mermaid_flowchart(
    mermaid: str,
    output_path: Optional[str] = None,
    theme: str = "light",
) -> str:
    """Import a Mermaid flowchart and convert to Excalidraw.

    Args:
        mermaid: Mermaid flowchart text
        output_path: Optional output file path
        theme: Color theme - "light" (default) or "dark"

    Returns:
        Result string containing the absolute path to the generated .excalidraw file
    """
    from .flowchart import FlowchartNode, FlowchartEdge
    from ..elements.text import create_labeled_shape, estimate_text_width
    from ..elements.arrows import create_arrow
    from ..elements.style import get_color
    from ..layout.sugiyama import sugiyama_layout

    direction = "LR"
    first_line = mermaid.strip().split("\n")[0].strip()
    dir_match = re.search(r"(?:graph|flowchart)\s+(LR|RL|TD|TB|BT)", first_line)
    if dir_match:
        d = dir_match.group(1)
        direction = "TB" if d == "TD" else d

    nodes, edges = parse_mermaid_flowchart(mermaid)

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
        from_label = next((n["label"] for n in nodes if n["id"] == e["from"]), e["from"])
        to_label = next((n["label"] for n in nodes if n["id"] == e["to"]), e["to"])
        fc_edges.append(FlowchartEdge(
            **{"from": from_label, "to": to_label},
            label=e.get("label"),
            style=e.get("style", "solid"),
        ))

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
    result_path = save_excalidraw(all_elements, path, theme=theme)
    return f"Mermaid flowchart imported to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"


def import_mermaid(
    mermaid: str,
    output_path: Optional[str] = None,
    theme: str = "light",
) -> str:
    """Import any Mermaid diagram and convert to Excalidraw.

    Auto-detects diagram type and generates the appropriate Excalidraw diagram.

    Args:
        mermaid: Mermaid diagram text
        output_path: Optional output file path
        theme: Color theme - "light" (default) or "dark"

    Returns:
        Result string containing the absolute path to the generated .excalidraw file
    """
    first_line = mermaid.strip().split("\n")[0].strip()

    if first_line.lower().startswith("pie"):
        from .pie_chart import create_pie_elements
        slices, pie_title = parse_mermaid_pie(mermaid)
        elements = create_pie_elements(slices, title=pie_title)
        path = output_path or "/tmp/mermaid-import.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Mermaid pie chart imported to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
    elif first_line.lower().startswith("sequencediagram"):
        from .sequence import create_sequence_elements
        participants, messages = parse_mermaid_sequence(mermaid)
        elements = create_sequence_elements(participants, messages)
        path = output_path or "/tmp/mermaid-import.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Mermaid sequence diagram imported to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
    elif first_line.lower().startswith("statediagram"):
        from .state_diagram import create_state_elements
        states, transitions = parse_mermaid_state(mermaid)
        elements = create_state_elements(states, transitions)
        path = output_path or "/tmp/mermaid-import.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Mermaid state diagram imported to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
    elif first_line.lower().startswith("classdiagram"):
        from .class_diagram import create_class_elements
        classes, rels = parse_mermaid_class(mermaid)
        elements = create_class_elements(classes, rels)
        path = output_path or "/tmp/mermaid-import.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Mermaid class diagram imported to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
    else:
        return import_mermaid_flowchart(mermaid=mermaid, output_path=output_path, theme=theme)


def register_mermaid_tools(mcp: FastMCP):
    @mcp.tool(name="import_mermaid_flowchart")
    def import_mermaid_flowchart_tool(
        mermaid: str,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Import a Mermaid flowchart and convert to Excalidraw.

        Parses Mermaid flowchart syntax and generates a hand-drawn
        Excalidraw diagram with Sugiyama layout.

        Args:
            mermaid: Mermaid flowchart text
            output_path: Optional output file path

        Returns:
            Absolute path to the generated .excalidraw file
        """
        return import_mermaid_flowchart(mermaid=mermaid, output_path=output_path, theme=theme)

    @mcp.tool(name="import_mermaid")
    def import_mermaid_tool(
        mermaid: str,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Import any Mermaid diagram and convert to Excalidraw.

        Auto-detects diagram type (flowchart or sequence diagram) and
        generates the appropriate Excalidraw diagram.

        Args:
            mermaid: Mermaid diagram text (flowchart or sequenceDiagram)
            output_path: Optional output file path

        Returns:
            Absolute path to the generated .excalidraw file
        """
        return import_mermaid(mermaid=mermaid, output_path=output_path, theme=theme)
