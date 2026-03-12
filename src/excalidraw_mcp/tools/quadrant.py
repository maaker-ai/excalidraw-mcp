"""Quadrant chart tool — generates 2x2 priority/positioning charts."""

import random
import time
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width
from ..elements.lines import create_line as _shared_create_line
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
CHART_SIZE = 500   # width and height of the chart area
MARGIN = 60        # margin around chart for labels
DOT_SIZE = 12


def _create_line(x1, y1, x2, y2, stroke_color="#868e96", stroke_width=2, stroke_style="solid"):
    """Create a line element. Delegates to shared utility."""
    return _shared_create_line(x1, y1, x2, y2, stroke_color=stroke_color, stroke_width=stroke_width, stroke_style=stroke_style)


def create_quadrant_elements(
    items: list[dict],
    x_label: str = "X Axis",
    y_label: str = "Y Axis",
    quadrant_labels: Optional[list[str]] = None,
    title: Optional[str] = None,
) -> list[dict]:
    """Create quadrant chart elements.

    Args:
        items: List of item dicts with 'label', 'x' (0-1), 'y' (0-1), optional 'color'
        x_label: X axis label
        y_label: Y axis label
        quadrant_labels: Optional 4 labels for quadrants [top-right, top-left, bottom-right, bottom-left]
        title: Optional chart title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []

    ox = MARGIN  # origin x
    oy = MARGIN + CHART_SIZE  # origin y (bottom-left of chart)

    # Draw axes
    # X axis (horizontal)
    x_axis = _create_line(ox, oy, ox + CHART_SIZE, oy, stroke_width=2)
    elements.append(x_axis)

    # Y axis (vertical)
    y_axis = _create_line(ox, oy, ox, oy - CHART_SIZE, stroke_width=2)
    elements.append(y_axis)

    # Midpoint lines (dashed)
    mid_h = _create_line(ox, oy - CHART_SIZE / 2, ox + CHART_SIZE, oy - CHART_SIZE / 2,
                         stroke_style="dashed", stroke_width=1, stroke_color="#ced4da")
    elements.append(mid_h)

    mid_v = _create_line(ox + CHART_SIZE / 2, oy, ox + CHART_SIZE / 2, oy - CHART_SIZE,
                         stroke_style="dashed", stroke_width=1, stroke_color="#ced4da")
    elements.append(mid_v)

    # Axis labels
    x_label_text = create_text(
        gen_id(), x_label,
        x=ox + CHART_SIZE / 2 - estimate_text_width(x_label, 14) / 2,
        y=oy + 15,
        font_size=14,
        width=estimate_text_width(x_label, 14),
        height=20,
    )
    elements.append(x_label_text)

    y_label_text = create_text(
        gen_id(), y_label,
        x=ox - estimate_text_width(y_label, 14) - 10,
        y=oy - CHART_SIZE / 2 - 10,
        font_size=14,
        width=estimate_text_width(y_label, 14),
        height=20,
    )
    elements.append(y_label_text)

    # Quadrant labels
    if quadrant_labels and len(quadrant_labels) >= 4:
        positions = [
            (ox + CHART_SIZE * 3 / 4, oy - CHART_SIZE * 3 / 4),  # top-right
            (ox + CHART_SIZE / 4, oy - CHART_SIZE * 3 / 4),       # top-left
            (ox + CHART_SIZE * 3 / 4, oy - CHART_SIZE / 4),       # bottom-right
            (ox + CHART_SIZE / 4, oy - CHART_SIZE / 4),            # bottom-left
        ]
        for ql, (qx, qy) in zip(quadrant_labels, positions):
            ql_width = estimate_text_width(ql, 12)
            ql_text = create_text(
                gen_id(), ql,
                x=qx - ql_width / 2,
                y=qy - 8,
                font_size=12,
                width=ql_width,
                height=16,
            )
            ql_text["opacity"] = 50  # subtle
            elements.append(ql_text)

    # Plot items
    colors_cycle = ["blue", "green", "purple", "orange", "red"]
    for idx, item in enumerate(items):
        label = item["label"]
        ix = item.get("x", 0.5)
        iy = item.get("y", 0.5)
        color_name = item.get("color", colors_cycle[idx % len(colors_cycle)])
        color = get_color(color_name)

        # Map 0-1 to chart coordinates
        px = ox + ix * CHART_SIZE
        py = oy - iy * CHART_SIZE  # invert y

        # Dot
        dot_id = gen_id()
        dot = {
            "id": dot_id,
            "type": "ellipse",
            "x": px - DOT_SIZE / 2,
            "y": py - DOT_SIZE / 2,
            "width": DOT_SIZE,
            "height": DOT_SIZE,
            "strokeColor": color["stroke"],
            "backgroundColor": color["bg"],
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
        elements.append(dot)

        # Label
        lw = estimate_text_width(label, 12)
        label_text = create_text(
            gen_id(), label,
            x=px - lw / 2,
            y=py + DOT_SIZE / 2 + 4,
            font_size=12,
            width=lw,
            height=16,
        )
        elements.append(label_text)

    # Title
    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title,
            x=ox + CHART_SIZE / 2 - title_width / 2,
            y=-10,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    return elements


class QuadrantItem(BaseModel):
    label: str = Field(description="Item label")
    x: float = Field(description="X position (0.0 to 1.0)")
    y: float = Field(description="Y position (0.0 to 1.0)")
    color: Optional[str] = Field(default=None, description="Color name")


def register_quadrant_tools(mcp: FastMCP):
    @mcp.tool()
    def create_quadrant_chart(
        items: list[QuadrantItem],
        x_label: str = "X Axis",
        y_label: str = "Y Axis",
        quadrant_labels: Optional[list[str]] = None,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a quadrant (2x2 matrix) chart.

        Generates a four-quadrant chart for positioning items along two axes.
        Great for priority matrices, effort/impact charts, and positioning maps.

        Args:
            items: List of items with label and x/y position (0-1 range)
            x_label: X axis label (e.g., "Effort")
            y_label: Y axis label (e.g., "Impact")
            quadrant_labels: Optional 4 labels [top-right, top-left, bottom-right, bottom-left]
            title: Optional chart title
            output_path: Optional output file path
            theme: Color theme - "light" or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        item_dicts = [
            {"label": i.label, "x": i.x, "y": i.y, "color": i.color}
            for i in items
        ]

        elements = create_quadrant_elements(
            item_dicts,
            x_label=x_label, y_label=y_label,
            quadrant_labels=quadrant_labels,
            title=title,
        )

        path = output_path or "/tmp/quadrant.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Quadrant chart saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
