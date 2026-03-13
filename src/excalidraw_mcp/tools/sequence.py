"""Sequence diagram tool — generates UML-style sequence diagrams."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width, create_centered_title
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
PARTICIPANT_GAP = 200       # horizontal gap between participant centers
PARTICIPANT_WIDTH = 150
PARTICIPANT_HEIGHT = 50
MESSAGE_GAP = 60            # vertical gap between messages
LIFELINE_START_OFFSET = 30  # gap between participant box bottom and first message
FONT_SIZE = 16
SELF_LOOP_WIDTH = 40        # width of self-message loop


def create_sequence_elements(
    participants: list[str],
    messages: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create sequence diagram elements.

    Args:
        participants: List of participant names
        messages: List of message dicts with 'from', 'to', 'label', optional 'style'
        title: Optional diagram title

    Returns:
        List of Excalidraw element dicts
    """
    import random
    import time

    elements = []
    participant_centers: dict[str, float] = {}

    # 1. Layout participants horizontally
    for idx, name in enumerate(participants):
        cx = idx * PARTICIPANT_GAP
        participant_centers[name] = cx

        # Participant box
        pw = max(estimate_text_width(name, FONT_SIZE) + 40, PARTICIPANT_WIDTH)
        px = cx - pw / 2
        py = 0

        shape, text = create_labeled_shape(
            "rectangle",
            id=gen_id(),
            label=name,
            x=px, y=py,
            width=pw, height=PARTICIPANT_HEIGHT,
            background_color="#a5d8ff",
            font_size=FONT_SIZE,
            stroke_color="#1971c2",
        )
        elements.extend([shape, text])

    # 2. Calculate lifeline length based on message count
    num_messages = len(messages)
    lifeline_length = LIFELINE_START_OFFSET + num_messages * MESSAGE_GAP + 40

    # 3. Draw lifelines (vertical dashed lines)
    for name, cx in participant_centers.items():
        line_id = gen_id()
        line_y = PARTICIPANT_HEIGHT
        line = {
            "id": line_id,
            "type": "line",
            "x": cx,
            "y": line_y,
            "width": 0,
            "height": lifeline_length,
            "strokeColor": "#868e96",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "dashed",
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
            "roundness": None,
            "points": [[0, 0], [0, lifeline_length]],
            "lastCommittedPoint": None,
            "startArrowhead": None,
            "endArrowhead": None,
            "startBinding": None,
            "endBinding": None,
        }
        elements.append(line)

    # 4. Draw messages (horizontal arrows between lifelines)
    for msg_idx, msg in enumerate(messages):
        from_name = msg["from"]
        to_name = msg["to"]
        label = msg.get("label", "")
        style = msg.get("style", "solid")

        from_x = participant_centers.get(from_name, 0)
        to_x = participant_centers.get(to_name, 0)

        msg_y = PARTICIPANT_HEIGHT + LIFELINE_START_OFFSET + msg_idx * MESSAGE_GAP

        if from_name == to_name:
            # Self-message: loop arrow going right and back
            arrow_id = gen_id()
            arrow = {
                "id": arrow_id,
                "type": "arrow",
                "x": from_x,
                "y": msg_y,
                "width": SELF_LOOP_WIDTH,
                "height": MESSAGE_GAP * 0.6,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": style,
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
                "points": [
                    [0, 0],
                    [SELF_LOOP_WIDTH, 0],
                    [SELF_LOOP_WIDTH, MESSAGE_GAP * 0.6],
                    [0, MESSAGE_GAP * 0.6],
                ],
                "lastCommittedPoint": None,
                "startArrowhead": None,
                "endArrowhead": "arrow",
                "startBinding": None,
                "endBinding": None,
            }
            elements.append(arrow)
        else:
            # Normal message arrow
            dx = to_x - from_x
            arrow_id = gen_id()
            arrow = {
                "id": arrow_id,
                "type": "arrow",
                "x": from_x,
                "y": msg_y,
                "width": abs(dx),
                "height": 0,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": style,
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
                "points": [[0, 0], [dx, 0]],
                "lastCommittedPoint": None,
                "startArrowhead": None,
                "endArrowhead": "arrow",
                "startBinding": None,
                "endBinding": None,
            }
            elements.append(arrow)

        # Message label text above the arrow
        if label:
            label_id = gen_id()
            label_width = estimate_text_width(label, FONT_SIZE - 2)
            mid_x = (from_x + to_x) / 2
            text_el = create_text(
                label_id, label,
                x=mid_x - label_width / 2,
                y=msg_y - FONT_SIZE * 1.4 - 2,
                font_size=FONT_SIZE - 2,
                width=label_width,
                height=(FONT_SIZE - 2) * 1.4,
            )
            elements.append(text_el)

    # 5. Title
    if title:
        elements.insert(0, create_centered_title(title, elements))

    return elements


def create_sequence_diagram(
    participants: list[str],
    messages: list[dict],
    title: Optional[str] = None,
    output_path: Optional[str] = None,
    theme: str = "light",
) -> str:
    """Create a UML-style sequence diagram and save to file.

    Args:
        participants: List of participant names (ordered left to right)
        messages: List of message dicts with from, to, label, and optional style
        title: Optional diagram title
        output_path: Optional output file path (default: /tmp/sequence.excalidraw)
        theme: Color theme - "light" (default) or "dark"

    Returns:
        Result string containing the absolute path to the generated .excalidraw file
    """
    elements = create_sequence_elements(participants, messages, title=title)
    path = output_path or "/tmp/sequence.excalidraw"
    result_path = save_excalidraw(elements, path, theme=theme)
    return f"Sequence diagram saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"


class SequenceMessage(BaseModel):
    from_participant: str = Field(alias="from", description="Source participant name")
    to_participant: str = Field(alias="to", description="Target participant name")
    label: str = Field(default="", description="Message label")
    style: str = Field(default="solid", description="Arrow style: solid or dashed (for return messages)")

    model_config = {"populate_by_name": True}


def register_sequence_tools(mcp: FastMCP):
    @mcp.tool(name="create_sequence_diagram")
    def create_sequence_diagram_tool(
        participants: list[str],
        messages: list[SequenceMessage],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a UML-style sequence diagram.

        Generates a hand-drawn style sequence diagram with participants,
        lifelines, and messages. Supports solid arrows for requests
        and dashed arrows for responses.

        Args:
            participants: List of participant names (ordered left to right)
            messages: List of messages with from, to, label, and optional style
            title: Optional diagram title
            output_path: Optional output file path (default: /tmp/sequence.excalidraw)

        Returns:
            Absolute path to the generated .excalidraw file
        """
        msg_dicts = [
            {"from": m.from_participant, "to": m.to_participant, "label": m.label, "style": m.style}
            for m in messages
        ]
        return create_sequence_diagram(participants, msg_dicts, title=title, output_path=output_path, theme=theme)
