"""User journey map tool — generates horizontal step-based journey maps."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width, create_centered_title
from ..elements.arrows import create_arrow
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
STEP_WIDTH = 180
STEP_HEIGHT = 80
STEP_GAP = 40
DESC_OFFSET = 20

# Emotion -> color mapping
EMOTION_COLORS = {
    "happy": "green",
    "excited": "green",
    "neutral": "blue",
    "confused": "yellow",
    "frustrated": "orange",
    "sad": "red",
    "angry": "red",
}


def create_journey_elements(
    steps: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create user journey map elements.

    Args:
        steps: List of step dicts with 'label', optional 'emotion', 'description'
        title: Optional journey title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    prev_shape = None

    for idx, step in enumerate(steps):
        label = step["label"]
        emotion = step.get("emotion", "neutral")
        description = step.get("description", "")
        color_name = EMOTION_COLORS.get(emotion, "blue")
        color = get_color(color_name)

        x = idx * (STEP_WIDTH + STEP_GAP)
        y = 0

        # Step box
        shape, text = create_labeled_shape(
            "rectangle",
            id=gen_id(),
            label=label,
            x=x, y=y,
            width=STEP_WIDTH, height=STEP_HEIGHT,
            background_color=color["bg"],
            stroke_color=color["stroke"],
            font_size=16,
        )
        shape["roundness"] = {"type": 3}
        elements.extend([shape, text])

        # Description below
        if description:
            desc_width = estimate_text_width(description, 12)
            desc_text = create_text(
                gen_id(), description,
                x=x + (STEP_WIDTH - desc_width) / 2,
                y=y + STEP_HEIGHT + DESC_OFFSET,
                font_size=12,
                width=desc_width,
                height=16,
            )
            desc_text["opacity"] = 70
            elements.append(desc_text)

        # Emotion emoji above
        emoji_map = {
            "happy": ":)",
            "excited": ":D",
            "neutral": ":|",
            "confused": ":?",
            "frustrated": ":/",
            "sad": ":(",
            "angry": ">:(",
        }
        emoji = emoji_map.get(emotion, ":|")
        emoji_text = create_text(
            gen_id(), emoji,
            x=x + STEP_WIDTH / 2 - 10,
            y=y - 25,
            font_size=16,
            width=20,
            height=22,
        )
        elements.append(emoji_text)

        # Arrow from previous step
        if prev_shape:
            arrow_elements = create_arrow(
                gen_id(), prev_shape, shape,
                strokeWidth=2,
            )
            elements.extend(arrow_elements)

        prev_shape = shape

    # Title
    if title:
        elements.insert(0, create_centered_title(title, elements))

    return elements


class JourneyStep(BaseModel):
    label: str = Field(description="Step name")
    emotion: str = Field(default="neutral", description="Emotion: happy, excited, neutral, confused, frustrated, sad, angry")
    description: Optional[str] = Field(default=None, description="Brief description of what happens at this step")


def register_user_journey_tools(mcp: FastMCP):
    @mcp.tool()
    def create_user_journey(
        steps: list[JourneyStep],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a user journey map.

        Generates a horizontal journey map showing steps with emotion indicators.
        Each step shows a label, emotion (color-coded), and optional description.

        Args:
            steps: List of journey steps with label and emotion
            title: Optional journey title
            output_path: Optional output file path
            theme: Color theme - "light" or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        step_dicts = [
            {"label": s.label, "emotion": s.emotion, "description": s.description or ""}
            for s in steps
        ]

        elements = create_journey_elements(step_dicts, title=title)

        path = output_path or "/tmp/user-journey.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"User journey saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
