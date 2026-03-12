"""SWOT analysis tool — generates 2x2 SWOT diagrams."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width
from ..elements.shapes import create_rectangle
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
QUADRANT_WIDTH = 300
QUADRANT_HEIGHT = 250
HEADER_HEIGHT = 40
ITEM_HEIGHT = 24
ITEM_FONT_SIZE = 14
HEADER_FONT_SIZE = 18
PADDING = 15

# SWOT color scheme
SWOT_COLORS = {
    "Strengths": "green",
    "Weaknesses": "red",
    "Opportunities": "blue",
    "Threats": "orange",
}


def create_swot_elements(
    data: dict,
    title: Optional[str] = None,
) -> list[dict]:
    """Create SWOT analysis elements.

    Args:
        data: Dict with keys 'strengths', 'weaknesses', 'opportunities', 'threats'
              Each is a list of strings.
        title: Optional diagram title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []

    quadrants = [
        ("Strengths", data.get("strengths", []), 0, 0),
        ("Weaknesses", data.get("weaknesses", []), QUADRANT_WIDTH, 0),
        ("Opportunities", data.get("opportunities", []), 0, QUADRANT_HEIGHT),
        ("Threats", data.get("threats", []), QUADRANT_WIDTH, QUADRANT_HEIGHT),
    ]

    for label, items, x, y in quadrants:
        color_name = SWOT_COLORS.get(label, "gray")
        color = get_color(color_name)

        # Background rectangle
        bg = create_rectangle(
            gen_id(),
            x, y, QUADRANT_WIDTH, QUADRANT_HEIGHT,
            background_color=color["bg"],
            stroke_color=color["stroke"],
            strokeWidth=2,
        )
        elements.append(bg)

        # Header text
        header_width = estimate_text_width(label, HEADER_FONT_SIZE)
        header_text = create_text(
            gen_id(), label,
            x=x + (QUADRANT_WIDTH - header_width) / 2,
            y=y + 10,
            font_size=HEADER_FONT_SIZE,
            width=header_width,
            height=HEADER_FONT_SIZE * 1.4,
        )
        elements.append(header_text)

        # Items
        for i, item in enumerate(items):
            bullet = f"• {item}"
            item_text = create_text(
                gen_id(), bullet,
                x=x + PADDING,
                y=y + HEADER_HEIGHT + 10 + i * ITEM_HEIGHT,
                font_size=ITEM_FONT_SIZE,
                width=estimate_text_width(bullet, ITEM_FONT_SIZE),
                height=ITEM_FONT_SIZE * 1.4,
            )
            elements.append(item_text)

    # Title
    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title,
            x=QUADRANT_WIDTH - title_width / 2,
            y=-50,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    return elements


class SWOTData(BaseModel):
    strengths: list[str] = Field(default_factory=list, description="List of strengths")
    weaknesses: list[str] = Field(default_factory=list, description="List of weaknesses")
    opportunities: list[str] = Field(default_factory=list, description="List of opportunities")
    threats: list[str] = Field(default_factory=list, description="List of threats")


def register_swot_tools(mcp: FastMCP):
    @mcp.tool()
    def create_swot_analysis(
        strengths: list[str] | None = None,
        weaknesses: list[str] | None = None,
        opportunities: list[str] | None = None,
        threats: list[str] | None = None,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a SWOT analysis diagram.

        Generates a color-coded 2x2 SWOT matrix with bullet-pointed items
        in each quadrant (Strengths, Weaknesses, Opportunities, Threats).

        Args:
            strengths: List of strength items
            weaknesses: List of weakness items
            opportunities: List of opportunity items
            threats: List of threat items
            title: Optional diagram title
            output_path: Optional output file path
            theme: Color theme

        Returns:
            Absolute path to the generated .excalidraw file
        """
        data = {
            "strengths": strengths or [],
            "weaknesses": weaknesses or [],
            "opportunities": opportunities or [],
            "threats": threats or [],
        }

        elements = create_swot_elements(data, title=title)

        path = output_path or "/tmp/swot.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"SWOT analysis saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
