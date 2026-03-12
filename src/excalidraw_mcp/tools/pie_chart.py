"""Pie chart tool — generates pie/donut charts."""

import math
import random
import time
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width
from ..elements.lines import create_line
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
RADIUS = 150
CENTER_X = 200
CENTER_Y = 200
LABEL_OFFSET = 40  # distance beyond radius for label

# Colors to cycle through for slices
SLICE_COLORS = ["blue", "green", "purple", "orange", "red", "pink", "yellow", "gray"]


def _create_line(x1, y1, x2, y2, stroke_color="#1e1e1e", stroke_width=2):
    """Create a line element. Delegates to shared utility."""
    return create_line(x1, y1, x2, y2, stroke_color=stroke_color, stroke_width=stroke_width)


def create_pie_elements(
    slices: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create pie chart elements.

    Args:
        slices: List of slice dicts with 'label', 'value', optional 'color'
        title: Optional chart title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []

    if not slices:
        return elements

    total = sum(s["value"] for s in slices)
    if total <= 0:
        return elements

    # Draw circle outline
    circle_id = gen_id()
    circle = {
        "id": circle_id,
        "type": "ellipse",
        "x": CENTER_X - RADIUS,
        "y": CENTER_Y - RADIUS,
        "width": RADIUS * 2,
        "height": RADIUS * 2,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
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
    elements.append(circle)

    # Draw slice dividers (lines from center to edge) and labels
    current_angle = -math.pi / 2  # start at top

    for idx, sl in enumerate(slices):
        label = sl["label"]
        value = sl["value"]
        color_name = sl.get("color", SLICE_COLORS[idx % len(SLICE_COLORS)])
        color = get_color(color_name)
        pct = value / total

        slice_angle = pct * 2 * math.pi

        # Dividing line from center to edge
        edge_x = CENTER_X + RADIUS * math.cos(current_angle)
        edge_y = CENTER_Y + RADIUS * math.sin(current_angle)
        line = _create_line(CENTER_X, CENTER_Y, edge_x, edge_y, stroke_color=color["stroke"])
        elements.append(line)

        # Label at midpoint of the slice arc, outside the circle
        mid_angle = current_angle + slice_angle / 2
        label_r = RADIUS + LABEL_OFFSET
        label_x = CENTER_X + label_r * math.cos(mid_angle)
        label_y = CENTER_Y + label_r * math.sin(mid_angle)

        pct_str = f"{pct * 100:.0f}%"
        display_label = f"{label} ({pct_str})"
        label_width = estimate_text_width(display_label, 14)
        label_text = create_text(
            gen_id(), display_label,
            x=label_x - label_width / 2,
            y=label_y - 10,
            font_size=14,
            width=label_width,
            height=20,
        )
        elements.append(label_text)

        current_angle += slice_angle

    # Final dividing line (closes the last slice)
    if len(slices) > 1:
        edge_x = CENTER_X + RADIUS * math.cos(current_angle)
        edge_y = CENTER_Y + RADIUS * math.sin(current_angle)
        line = _create_line(CENTER_X, CENTER_Y, edge_x, edge_y)
        elements.append(line)

    # Title
    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title,
            x=CENTER_X - title_width / 2,
            y=-30,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    return elements


class PieSlice(BaseModel):
    label: str = Field(description="Slice label")
    value: float = Field(description="Slice value (proportional)")
    color: Optional[str] = Field(default=None, description="Color name")


def register_pie_chart_tools(mcp: FastMCP):
    @mcp.tool()
    def create_pie_chart(
        slices: list[PieSlice],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a pie chart diagram.

        Generates a pie chart with labeled slices showing proportions.
        Each slice displays its label and percentage.

        Args:
            slices: List of slices with label and value
            title: Optional chart title
            output_path: Optional output file path
            theme: Color theme - "light" or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        slice_dicts = [
            {"label": s.label, "value": s.value, "color": s.color}
            for s in slices
        ]

        elements = create_pie_elements(slice_dicts, title=title)

        path = output_path or "/tmp/pie-chart.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Pie chart saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
