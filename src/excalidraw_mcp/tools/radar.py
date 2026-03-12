"""Radar/spider chart tool."""

import math
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width
from ..elements.lines import create_line
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
RADIUS = 180
CENTER_X = 250
CENTER_Y = 250
LABEL_OFFSET = 30

SERIES_COLORS = ["blue", "red", "green", "purple", "orange"]


def create_radar_elements(
    axes: list[str],
    values: Optional[list[float]] = None,
    series: Optional[list[dict]] = None,
    title: Optional[str] = None,
) -> list[dict]:
    """Create radar/spider chart elements.

    Args:
        axes: List of axis names
        values: Single set of values (0-1 range), one per axis
        series: Multiple sets: [{"label": "A", "values": [0.5, 0.8, ...]}]
        title: Optional chart title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    n = len(axes)
    if n < 3:
        return elements

    angle_step = 2 * math.pi / n

    # Draw grid rings (concentric pentagons/polygons)
    for level in [0.25, 0.5, 0.75, 1.0]:
        r = RADIUS * level
        for i in range(n):
            angle1 = -math.pi / 2 + i * angle_step
            angle2 = -math.pi / 2 + (i + 1) * angle_step
            x1 = CENTER_X + r * math.cos(angle1)
            y1 = CENTER_Y + r * math.sin(angle1)
            x2 = CENTER_X + r * math.cos(angle2)
            y2 = CENTER_Y + r * math.sin(angle2)
            line = create_line(x1, y1, x2, y2, stroke_color="#dee2e6", stroke_width=1)
            elements.append(line)

    # Draw axis lines
    for i in range(n):
        angle = -math.pi / 2 + i * angle_step
        ex = CENTER_X + RADIUS * math.cos(angle)
        ey = CENTER_Y + RADIUS * math.sin(angle)
        axis_line = create_line(CENTER_X, CENTER_Y, ex, ey, stroke_color="#adb5bd", stroke_width=1)
        elements.append(axis_line)

        # Axis label
        lx = CENTER_X + (RADIUS + LABEL_OFFSET) * math.cos(angle)
        ly = CENTER_Y + (RADIUS + LABEL_OFFSET) * math.sin(angle)
        lw = estimate_text_width(axes[i], 13)
        label = create_text(
            gen_id(), axes[i],
            x=lx - lw / 2, y=ly - 8,
            font_size=13, width=lw, height=18,
        )
        elements.append(label)

    # Build series list
    all_series = []
    if values:
        all_series.append({"label": "", "values": values})
    if series:
        all_series.extend(series)

    # Draw data polygons
    for s_idx, s in enumerate(all_series):
        vals = s["values"]
        color_name = SERIES_COLORS[s_idx % len(SERIES_COLORS)]
        color = get_color(color_name)

        for i in range(n):
            v1 = vals[i] if i < len(vals) else 0
            v2 = vals[(i + 1) % n] if (i + 1) % n < len(vals) else 0
            angle1 = -math.pi / 2 + i * angle_step
            angle2 = -math.pi / 2 + ((i + 1) % n) * angle_step
            x1 = CENTER_X + RADIUS * v1 * math.cos(angle1)
            y1 = CENTER_Y + RADIUS * v1 * math.sin(angle1)
            x2 = CENTER_X + RADIUS * v2 * math.cos(angle2)
            y2 = CENTER_Y + RADIUS * v2 * math.sin(angle2)
            data_line = create_line(x1, y1, x2, y2, stroke_color=color["stroke"], stroke_width=2)
            elements.append(data_line)

    # Title
    if title:
        tw = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title,
            x=CENTER_X - tw / 2, y=-10,
            font_size=24, width=tw,
        )
        elements.insert(0, title_text)

    return elements


class RadarSeries(BaseModel):
    label: str = Field(description="Series label")
    values: list[float] = Field(description="Values (0-1 range), one per axis")


def register_radar_tools(mcp: FastMCP):
    @mcp.tool()
    def create_radar_chart(
        axes: list[str],
        values: Optional[list[float]] = None,
        series: Optional[list[RadarSeries]] = None,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a radar/spider chart.

        Generates a radar chart with axes radiating from center.
        Supports single or multiple data series overlay.

        Args:
            axes: List of axis names (minimum 3)
            values: Single set of values (0-1), one per axis
            series: Multiple series for comparison
            title: Optional chart title
            output_path: Optional output file path
            theme: Color theme

        Returns:
            Absolute path to the generated .excalidraw file
        """
        series_dicts = None
        if series:
            series_dicts = [{"label": s.label, "values": s.values} for s in series]

        elements = create_radar_elements(axes, values=values, series=series_dicts, title=title)

        path = output_path or "/tmp/radar.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Radar chart saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
