"""Timeline / Gantt chart tool — generates horizontal bar timelines."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
UNIT_WIDTH = 80          # pixels per time unit
BAR_HEIGHT = 40          # height of each bar
ROW_GAP = 10             # vertical gap between rows
LABEL_MARGIN = 10        # left margin for label inside bar
HEADER_HEIGHT = 60       # space above bars for time axis


def create_timeline_elements(
    events: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create timeline/Gantt elements.

    Args:
        events: List of event dicts with 'label', 'start', 'end', optional 'color'
        title: Optional diagram title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []

    if not events:
        return elements

    # Default color cycle
    default_colors = ["blue", "green", "purple", "orange", "red", "pink"]

    # Assign rows to avoid overlapping bars
    rows: list[list[dict]] = []
    for evt in events:
        placed = False
        for row in rows:
            # Check if event overlaps with any in this row
            overlap = any(
                not (evt["end"] <= existing["start"] or evt["start"] >= existing["end"])
                for existing in row
            )
            if not overlap:
                row.append(evt)
                evt["_row"] = rows.index(row)
                placed = True
                break
        if not placed:
            evt["_row"] = len(rows)
            rows.append([evt])

    # Find time range
    min_start = min(e["start"] for e in events)
    max_end = max(e["end"] for e in events)

    # Draw time axis markers
    for t in range(int(min_start), int(max_end) + 1):
        x = (t - min_start) * UNIT_WIDTH
        marker_text = create_text(
            gen_id(), str(t),
            x=x - 5, y=HEADER_HEIGHT - 25,
            font_size=12,
            width=20, height=16,
        )
        elements.append(marker_text)

    # Draw event bars
    for idx, evt in enumerate(events):
        label = evt["label"]
        start = evt["start"]
        end = evt["end"]
        row = evt["_row"]
        color_name = evt.get("color", default_colors[idx % len(default_colors)])
        color = get_color(color_name)

        x = (start - min_start) * UNIT_WIDTH
        y = HEADER_HEIGHT + row * (BAR_HEIGHT + ROW_GAP)
        width = (end - start) * UNIT_WIDTH
        height = BAR_HEIGHT

        shape, text = create_labeled_shape(
            "rectangle",
            id=gen_id(),
            label=label,
            x=x, y=y,
            width=max(width, 40), height=height,
            background_color=color["bg"],
            stroke_color=color["stroke"],
            font_size=14,
        )
        elements.extend([shape, text])

    # Title
    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title, x=0, y=-40,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    # Clean up temp keys
    for evt in events:
        evt.pop("_row", None)

    return elements


class TimelineEvent(BaseModel):
    label: str = Field(description="Event/task label")
    start: float = Field(description="Start time (numeric, e.g. week number, month, or arbitrary unit)")
    end: float = Field(description="End time (must be > start)")
    color: Optional[str] = Field(default=None, description="Color name")


def register_timeline_tools(mcp: FastMCP):
    @mcp.tool()
    def create_timeline(
        events: list[TimelineEvent],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a timeline / Gantt chart diagram.

        Generates a horizontal bar chart showing events/tasks over time.
        Overlapping events are automatically placed on separate rows.

        Args:
            events: List of events with label, start, end, and optional color
            title: Optional diagram title
            output_path: Optional output file path (default: /tmp/timeline.excalidraw)
            theme: Color theme - "light" or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        evt_dicts = [
            {"label": e.label, "start": e.start, "end": e.end, "color": e.color or "blue"}
            for e in events
        ]

        elements = create_timeline_elements(evt_dicts, title=title)

        path = output_path or "/tmp/timeline.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Timeline saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
