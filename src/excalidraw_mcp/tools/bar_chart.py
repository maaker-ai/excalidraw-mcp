"""Bar chart tool — generates vertical bar charts."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width
from ..elements.shapes import create_rectangle
from ..elements.lines import create_line
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
BAR_WIDTH = 50
BAR_GAP = 20
CHART_HEIGHT = 300
AXIS_MARGIN = 40
LABEL_OFFSET = 15

DEFAULT_COLORS = ["blue", "green", "purple", "orange", "red", "pink", "yellow"]


def create_bar_elements(
    bars: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create bar chart elements.

    Args:
        bars: List of bar dicts with 'label', 'value', optional 'color'
        title: Optional chart title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []

    if not bars:
        return elements

    max_value = max(b["value"] for b in bars)
    if max_value <= 0:
        max_value = 1

    # Draw axes
    total_width = len(bars) * (BAR_WIDTH + BAR_GAP) - BAR_GAP + AXIS_MARGIN * 2
    origin_x = AXIS_MARGIN
    origin_y = CHART_HEIGHT

    # Y axis
    y_axis = create_line(origin_x, 0, origin_x, origin_y, stroke_color="#868e96")
    elements.append(y_axis)

    # X axis
    x_axis = create_line(origin_x, origin_y, origin_x + total_width - AXIS_MARGIN, origin_y, stroke_color="#868e96")
    elements.append(x_axis)

    # Draw bars
    for idx, bar in enumerate(bars):
        label = bar["label"]
        value = bar["value"]
        color_name = bar.get("color", DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])
        color = get_color(color_name)

        bar_height = (value / max_value) * (CHART_HEIGHT - 20)
        x = origin_x + AXIS_MARGIN + idx * (BAR_WIDTH + BAR_GAP)
        y = origin_y - bar_height

        rect = create_rectangle(
            gen_id(), x, y, BAR_WIDTH, bar_height,
            background_color=color["bg"],
            stroke_color=color["stroke"],
        )
        elements.append(rect)

        # Value label above bar
        val_str = str(int(value)) if value == int(value) else f"{value:.1f}"
        vw = estimate_text_width(val_str, 12)
        val_text = create_text(
            gen_id(), val_str,
            x=x + BAR_WIDTH / 2 - vw / 2,
            y=y - 18,
            font_size=12, width=vw, height=16,
        )
        elements.append(val_text)

        # X-axis label below bar
        lw = estimate_text_width(label, 12)
        label_text = create_text(
            gen_id(), label,
            x=x + BAR_WIDTH / 2 - lw / 2,
            y=origin_y + LABEL_OFFSET,
            font_size=12, width=lw, height=16,
        )
        elements.append(label_text)

    # Title
    if title:
        tw = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title, x=total_width / 2 - tw / 2, y=-40,
            font_size=24, width=tw,
        )
        elements.insert(0, title_text)

    return elements


class BarData(BaseModel):
    label: str = Field(description="Bar label")
    value: float = Field(description="Bar value")
    color: Optional[str] = Field(default=None, description="Color name")


def register_bar_chart_tools(mcp: FastMCP):
    @mcp.tool()
    def create_bar_chart(
        bars: list[BarData],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a vertical bar chart.

        Generates a bar chart with auto-scaled bars, value labels,
        and axis labels.

        Args:
            bars: List of bars with label and value
            title: Optional chart title
            output_path: Optional output file path
            theme: Color theme

        Returns:
            Absolute path to the generated .excalidraw file
        """
        bar_dicts = [
            {"label": b.label, "value": b.value, "color": b.color}
            for b in bars
        ]

        elements = create_bar_elements(bar_dicts, title=title)

        path = output_path or "/tmp/bar-chart.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Bar chart saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
