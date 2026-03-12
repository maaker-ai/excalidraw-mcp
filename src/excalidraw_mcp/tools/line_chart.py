"""Line chart tool — generates line charts with one or more series."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width
from ..elements.lines import create_line
from ..elements.shapes import create_ellipse, create_rectangle
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
CHART_WIDTH = 500
CHART_HEIGHT = 300
AXIS_MARGIN = 50
LABEL_OFFSET = 15

SERIES_COLORS = ["blue", "red", "green", "purple", "orange", "pink", "yellow"]


def create_line_chart_elements(
    series: list[dict],
    x_labels: list[str],
    title: Optional[str] = None,
) -> list[dict]:
    """Create line chart elements.

    Args:
        series: List of series dicts with 'label' and 'points' (list of numbers)
        x_labels: Labels for the X axis
        title: Optional chart title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []

    if not series or not x_labels:
        return elements

    n_points = len(x_labels)

    # Find global max value for scaling
    all_values = []
    for s in series:
        all_values.extend(s["points"][:n_points])
    max_value = max(all_values) if all_values else 1
    if max_value <= 0:
        max_value = 1

    origin_x = AXIS_MARGIN
    origin_y = CHART_HEIGHT

    # Y axis
    elements.append(create_line(origin_x, 0, origin_x, origin_y, stroke_color="#868e96"))

    # X axis
    elements.append(create_line(origin_x, origin_y, origin_x + CHART_WIDTH, origin_y, stroke_color="#868e96"))

    # X step
    x_step = CHART_WIDTH / max(n_points - 1, 1)

    # X-axis labels
    for i, label in enumerate(x_labels):
        lx = origin_x + i * x_step
        lw = estimate_text_width(label, 12)
        label_text = create_text(
            gen_id(), label,
            x=lx - lw / 2,
            y=origin_y + LABEL_OFFSET,
            font_size=12, width=lw, height=16,
        )
        elements.append(label_text)

    # Draw each series
    for s_idx, s in enumerate(series):
        points = s["points"][:n_points]
        color_name = SERIES_COLORS[s_idx % len(SERIES_COLORS)]
        color = get_color(color_name)

        # Calculate coordinates
        coords = []
        for i, val in enumerate(points):
            px = origin_x + i * x_step
            py = origin_y - (val / max_value) * (CHART_HEIGHT - 20)
            coords.append((px, py))

        # Draw line segments
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            seg = create_line(x1, y1, x2, y2, stroke_color=color["stroke"], stroke_width=2)
            elements.append(seg)

        # Draw data point markers
        MARKER_SIZE = 8
        for px, py in coords:
            marker = create_ellipse(
                gen_id(),
                px - MARKER_SIZE / 2, py - MARKER_SIZE / 2,
                MARKER_SIZE, MARKER_SIZE,
                background_color=color["stroke"],
                stroke_color=color["stroke"],
            )
            elements.append(marker)

    # Legend (only for multi-series)
    if len(series) > 1:
        legend_x = origin_x + CHART_WIDTH + 20
        legend_y = 10
        for s_idx, s in enumerate(series):
            color_name = SERIES_COLORS[s_idx % len(SERIES_COLORS)]
            color = get_color(color_name)
            # Color swatch line
            swatch = create_line(
                legend_x, legend_y + 8,
                legend_x + 20, legend_y + 8,
                stroke_color=color["stroke"], stroke_width=3,
            )
            elements.append(swatch)
            # Label
            lbl = s.get("label", f"Series {s_idx + 1}")
            lw = estimate_text_width(lbl, 12)
            legend_text = create_text(
                gen_id(), lbl,
                x=legend_x + 25, y=legend_y,
                font_size=12, width=lw, height=16,
            )
            elements.append(legend_text)
            legend_y += 22

    # Title
    if title:
        tw = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title,
            x=(AXIS_MARGIN + CHART_WIDTH) / 2 - tw / 2, y=-40,
            font_size=24, width=tw,
        )
        elements.insert(0, title_text)

    return elements


class LineSeriesData(BaseModel):
    label: str = Field(description="Series label")
    points: list[float] = Field(description="Data points (numbers)")


def register_line_chart_tools(mcp: FastMCP):
    @mcp.tool()
    def create_line_chart(
        series: list[LineSeriesData],
        x_labels: list[str],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a line chart with one or more data series.

        Generates a line chart with auto-scaled Y axis, X-axis labels,
        and color-coded series.

        Args:
            series: List of data series with label and points
            x_labels: Labels for the X axis
            title: Optional chart title
            output_path: Optional output file path
            theme: Color theme

        Returns:
            Absolute path to the generated .excalidraw file
        """
        series_dicts = [
            {"label": s.label, "points": s.points}
            for s in series
        ]

        elements = create_line_chart_elements(series_dicts, x_labels, title=title)

        path = output_path or "/tmp/line-chart.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Line chart saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
