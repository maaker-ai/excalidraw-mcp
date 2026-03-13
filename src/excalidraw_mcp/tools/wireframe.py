"""Wireframe tool — generates simple UI mockup wireframes."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width, create_centered_title
from ..elements.shapes import create_rectangle
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
FRAME_WIDTH = 375       # iPhone-style width
FRAME_HEIGHT = 667      # iPhone-style height
PADDING = 20
COMPONENT_GAP = 15
HEADER_HEIGHT = 50
BUTTON_HEIGHT = 44
INPUT_HEIGHT = 40
TEXT_HEIGHT = 24
IMAGE_HEIGHT = 150
CARD_HEIGHT = 100
NAV_HEIGHT = 50


def create_wireframe_elements(
    components: list[dict],
    device: str = "none",
    title: Optional[str] = None,
) -> list[dict]:
    """Create wireframe UI mockup elements.

    Args:
        components: List of component dicts with 'type' and 'label'
                   Types: header, text, button, input, image, card, nav, divider
        device: Device frame: "none", "phone", "tablet", "desktop"
        title: Optional wireframe title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []

    # Device frame
    frame_x = 0
    frame_y = 0
    content_x = PADDING
    content_width = FRAME_WIDTH - PADDING * 2

    if device == "phone":
        frame_width = FRAME_WIDTH
        frame_height = FRAME_HEIGHT
    elif device == "tablet":
        frame_width = 768
        frame_height = 1024
        content_width = frame_width - PADDING * 2
    elif device == "desktop":
        frame_width = 1024
        frame_height = 768
        content_width = frame_width - PADDING * 2
    else:
        frame_width = FRAME_WIDTH
        frame_height = FRAME_HEIGHT

    if device != "none":
        # Outer device frame
        frame = create_rectangle(
            gen_id(),
            frame_x, frame_y, frame_width, frame_height,
            background_color="#ffffff",
            stroke_color="#343a40",
            strokeWidth=2,
        )
        frame["roundness"] = {"type": 3}
        elements.append(frame)

        # Status bar
        status_bar = create_rectangle(
            gen_id(),
            frame_x, frame_y, frame_width, 30,
            background_color="#f1f3f5",
            stroke_color="#dee2e6",
            strokeWidth=1,
        )
        elements.append(status_bar)

        content_y = 40  # below status bar
    else:
        content_y = 0

    # Render components
    current_y = content_y

    for comp in components:
        comp_type = comp.get("type", "text")
        label = comp.get("label", "")

        if comp_type == "header":
            shape, text = create_labeled_shape(
                "rectangle",
                id=gen_id(),
                label=label,
                x=frame_x, y=current_y,
                width=frame_width if device != "none" else content_width + PADDING * 2,
                height=HEADER_HEIGHT,
                background_color="#e9ecef",
                stroke_color="#adb5bd",
                font_size=18,
            )
            elements.extend([shape, text])
            current_y += HEADER_HEIGHT + COMPONENT_GAP

        elif comp_type == "button":
            btn_width = min(estimate_text_width(label, 16) + 40, content_width)
            shape, text = create_labeled_shape(
                "rectangle",
                id=gen_id(),
                label=label,
                x=content_x + (content_width - btn_width) / 2,
                y=current_y,
                width=btn_width,
                height=BUTTON_HEIGHT,
                background_color="#228be6",
                stroke_color="#1971c2",
                font_size=16,
            )
            shape["roundness"] = {"type": 3}
            elements.extend([shape, text])
            current_y += BUTTON_HEIGHT + COMPONENT_GAP

        elif comp_type == "input":
            shape, text = create_labeled_shape(
                "rectangle",
                id=gen_id(),
                label=label,
                x=content_x, y=current_y,
                width=content_width, height=INPUT_HEIGHT,
                background_color="#ffffff",
                stroke_color="#ced4da",
                font_size=14,
            )
            shape["roundness"] = {"type": 3}
            elements.extend([shape, text])
            current_y += INPUT_HEIGHT + COMPONENT_GAP

        elif comp_type == "image":
            # Placeholder image box with X
            shape = create_rectangle(
                gen_id(),
                content_x, current_y, content_width, IMAGE_HEIGHT,
                background_color="#f8f9fa",
                stroke_color="#adb5bd",
            )
            elements.append(shape)
            # "Image" text in center
            img_label = create_text(
                gen_id(), label or "Image",
                x=content_x + content_width / 2 - 25,
                y=current_y + IMAGE_HEIGHT / 2 - 10,
                font_size=14,
                width=50, height=20,
            )
            img_label["opacity"] = 50
            elements.append(img_label)
            current_y += IMAGE_HEIGHT + COMPONENT_GAP

        elif comp_type == "card":
            shape, text = create_labeled_shape(
                "rectangle",
                id=gen_id(),
                label=label,
                x=content_x, y=current_y,
                width=content_width, height=CARD_HEIGHT,
                background_color="#ffffff",
                stroke_color="#dee2e6",
                font_size=14,
            )
            shape["roundness"] = {"type": 3}
            elements.extend([shape, text])
            current_y += CARD_HEIGHT + COMPONENT_GAP

        elif comp_type == "nav":
            shape, text = create_labeled_shape(
                "rectangle",
                id=gen_id(),
                label=label,
                x=frame_x, y=current_y,
                width=frame_width if device != "none" else content_width + PADDING * 2,
                height=NAV_HEIGHT,
                background_color="#f1f3f5",
                stroke_color="#dee2e6",
                font_size=14,
            )
            elements.extend([shape, text])
            current_y += NAV_HEIGHT + COMPONENT_GAP

        elif comp_type == "divider":
            import random
            import time
            div_id = gen_id()
            divider = {
                "id": div_id,
                "type": "line",
                "x": content_x, "y": current_y + 5,
                "width": content_width, "height": 0,
                "strokeColor": "#dee2e6",
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
                "roundness": None,
                "points": [[0, 0], [content_width, 0]],
                "lastCommittedPoint": None,
                "startArrowhead": None,
                "endArrowhead": None,
                "startBinding": None,
                "endBinding": None,
            }
            elements.append(divider)
            current_y += 10 + COMPONENT_GAP

        else:
            # Default: text block
            text_el = create_text(
                gen_id(), label,
                x=content_x,
                y=current_y,
                font_size=14,
                width=estimate_text_width(label, 14),
                height=TEXT_HEIGHT,
            )
            elements.append(text_el)
            current_y += TEXT_HEIGHT + COMPONENT_GAP

    # Title
    if title:
        elements.insert(0, create_centered_title(title, elements))

    return elements


class WireframeComponent(BaseModel):
    type: str = Field(description="Component type: header, text, button, input, image, card, nav, divider")
    label: str = Field(default="", description="Component label/text")


def register_wireframe_tools(mcp: FastMCP):
    @mcp.tool()
    def create_wireframe(
        components: list[WireframeComponent],
        device: str = "phone",
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a wireframe UI mockup.

        Generates a simple wireframe with common UI components stacked
        vertically. Great for quick screen mockups and UI planning.

        Component types:
        - header: Full-width header bar
        - text: Plain text block
        - button: Centered button
        - input: Text input field
        - image: Image placeholder
        - card: Content card
        - nav: Navigation bar
        - divider: Horizontal line

        Args:
            components: List of UI components in order
            device: Device frame: "phone", "tablet", "desktop", "none"
            title: Optional wireframe title
            output_path: Optional output file path
            theme: Color theme

        Returns:
            Absolute path to the generated .excalidraw file
        """
        comp_dicts = [{"type": c.type, "label": c.label} for c in components]

        elements = create_wireframe_elements(comp_dicts, device=device, title=title)

        path = output_path or "/tmp/wireframe.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Wireframe saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
