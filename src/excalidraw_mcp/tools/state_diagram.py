"""State diagram tool — generates UML-style state machine diagrams."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width
from ..elements.arrows import create_arrow
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
STATE_GAP = 250
STATE_WIDTH = 160
STATE_HEIGHT = 50
INITIAL_SIZE = 30     # diameter of initial state circle
FONT_SIZE = 16


def create_state_elements(
    states: list[dict],
    transitions: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create state diagram elements.

    Args:
        states: List of state dicts with 'name', optional 'is_initial', 'is_final', 'color'
        transitions: List of transition dicts with 'from', 'to', 'label'
        title: Optional diagram title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    state_shapes = {}

    # Layout states in a grid-like arrangement
    cols = max(3, int(len(states) ** 0.5) + 1)
    for idx, state in enumerate(states):
        name = state["name"]
        is_initial = state.get("is_initial", False)
        is_final = state.get("is_final", False)
        color_name = state.get("color", "blue")
        color = get_color(color_name)

        col = idx % cols
        row = idx // cols
        x = col * STATE_GAP
        y = row * (STATE_HEIGHT + 80)

        if is_initial:
            # Small filled circle for initial state
            shape_id = gen_id()
            import random
            import time
            ellipse = {
                "id": shape_id,
                "type": "ellipse",
                "x": x + STATE_WIDTH / 2 - INITIAL_SIZE / 2,
                "y": y + STATE_HEIGHT / 2 - INITIAL_SIZE / 2,
                "width": INITIAL_SIZE,
                "height": INITIAL_SIZE,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "#1e1e1e",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "angle": 0,
                "seed": random.randint(1, 2**31),
                "version": 1,
                "versionNonce": random.randint(1, 2**31),
                "isDeleted": False,
                "groupIds": [],
                "boundElements": [],
                "updated": int(time.time() * 1000),
                "link": None,
                "locked": False,
                "roundness": {"type": 2},
            }
            elements.append(ellipse)
            state_shapes[name] = ellipse
        else:
            # Regular state: rounded rectangle
            shape, text = create_labeled_shape(
                "rectangle",
                id=gen_id(),
                label=name,
                x=x, y=y,
                width=STATE_WIDTH, height=STATE_HEIGHT,
                background_color=color["bg"],
                stroke_color=color["stroke"],
                font_size=FONT_SIZE,
            )
            # Add roundness for state diagrams
            shape["roundness"] = {"type": 3}
            elements.extend([shape, text])
            state_shapes[name] = shape

            # Add double border for final states
            if is_final:
                inner_id = gen_id()
                import random
                import time
                inner = {
                    "id": inner_id,
                    "type": "rectangle",
                    "x": x + 4,
                    "y": y + 4,
                    "width": STATE_WIDTH - 8,
                    "height": STATE_HEIGHT - 8,
                    "strokeColor": color["stroke"],
                    "backgroundColor": "transparent",
                    "fillStyle": "solid",
                    "strokeWidth": 1,
                    "strokeStyle": "solid",
                    "roughness": 0,
                    "opacity": 100,
                    "angle": 0,
                    "seed": random.randint(1, 2**31),
                    "version": 1,
                    "versionNonce": random.randint(1, 2**31),
                    "isDeleted": False,
                    "groupIds": [],
                    "boundElements": [],
                    "updated": int(time.time() * 1000),
                    "link": None,
                    "locked": False,
                    "roundness": {"type": 3},
                }
                elements.append(inner)

    # Transitions
    for trans in transitions:
        from_name = trans["from"]
        to_name = trans["to"]
        label = trans.get("label", "")

        from_shape = state_shapes.get(from_name)
        to_shape = state_shapes.get(to_name)
        if from_shape and to_shape:
            result = create_arrow(
                gen_id(), from_shape, to_shape,
                label=label if label else None,
            )
            elements.extend(result)

    # Title
    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title, x=0, y=-50,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    return elements


class StateDef(BaseModel):
    name: str = Field(description="State name")
    is_initial: bool = Field(default=False, description="Whether this is the initial state (shown as filled circle)")
    is_final: bool = Field(default=False, description="Whether this is a final/accepting state (shown with double border)")
    color: Optional[str] = Field(default=None, description="Color name")


class StateTransition(BaseModel):
    from_state: str = Field(alias="from", description="Source state name")
    to_state: str = Field(alias="to", description="Target state name")
    label: str = Field(default="", description="Transition label (event/action)")

    model_config = {"populate_by_name": True}


def register_state_diagram_tools(mcp: FastMCP):
    @mcp.tool()
    def create_state_diagram(
        states: list[StateDef],
        transitions: list[StateTransition],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a UML state machine diagram.

        Generates a state diagram with states (rounded rectangles),
        initial states (filled circles), final states (double border),
        and transition arrows with labels.

        Args:
            states: List of state definitions
            transitions: List of transitions between states
            title: Optional diagram title
            output_path: Optional output file path
            theme: Color theme - "light" or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        state_dicts = [
            {"name": s.name, "is_initial": s.is_initial, "is_final": s.is_final, "color": s.color or "blue"}
            for s in states
        ]

        trans_dicts = [
            {"from": t.from_state, "to": t.to_state, "label": t.label}
            for t in transitions
        ]

        elements = create_state_elements(state_dicts, trans_dicts, title=title)

        path = output_path or "/tmp/state-diagram.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"State diagram saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
