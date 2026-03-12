"""Kanban board tool — generates column-based task boards."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width
from ..elements.shapes import create_rectangle
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
COLUMN_WIDTH = 220
COLUMN_GAP = 30
CARD_HEIGHT = 50
CARD_GAP = 10
CARD_PADDING = 10
HEADER_HEIGHT = 45
COLUMN_PADDING = 15


def create_kanban_elements(
    columns: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create kanban board elements.

    Args:
        columns: List of column dicts with 'name', 'cards' (list of strings), optional 'color'
        title: Optional board title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    default_colors = ["gray", "blue", "green", "purple", "orange"]

    for col_idx, col in enumerate(columns):
        name = col["name"]
        cards = col.get("cards", [])
        color_name = col.get("color", default_colors[col_idx % len(default_colors)])
        color = get_color(color_name)

        x = col_idx * (COLUMN_WIDTH + COLUMN_GAP)

        # Column height based on cards
        num_cards = max(len(cards), 1)  # min height for empty columns
        column_height = HEADER_HEIGHT + COLUMN_PADDING + num_cards * (CARD_HEIGHT + CARD_GAP) + COLUMN_PADDING

        # Column background
        col_bg_id = gen_id()
        col_bg = create_rectangle(
            col_bg_id,
            x, 0, COLUMN_WIDTH, column_height,
            background_color=color["bg"],
            stroke_color=color["stroke"],
            strokeWidth=1,
        )
        col_bg["roundness"] = {"type": 3}
        elements.append(col_bg)

        # Column header text
        header_text = create_text(
            gen_id(), name,
            x=x + (COLUMN_WIDTH - estimate_text_width(name, 16)) / 2,
            y=12,
            font_size=16,
            width=estimate_text_width(name, 16),
            height=22,
        )
        elements.append(header_text)

        # Cards
        card_y = HEADER_HEIGHT + COLUMN_PADDING
        for card_text in cards:
            card_x = x + CARD_PADDING
            card_w = COLUMN_WIDTH - CARD_PADDING * 2

            card_shape, card_label = create_labeled_shape(
                "rectangle",
                id=gen_id(),
                label=card_text,
                x=card_x, y=card_y,
                width=card_w, height=CARD_HEIGHT,
                background_color="#ffffff",
                stroke_color="#dee2e6",
                font_size=14,
            )
            card_shape["roundness"] = {"type": 3}
            elements.extend([card_shape, card_label])

            card_y += CARD_HEIGHT + CARD_GAP

    # Title
    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title, x=0, y=-50,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    return elements


class KanbanColumn(BaseModel):
    name: str = Field(description="Column name (e.g., 'To Do', 'In Progress', 'Done')")
    cards: list[str] = Field(default_factory=list, description="List of card labels")
    color: Optional[str] = Field(default=None, description="Column color name")


def register_kanban_tools(mcp: FastMCP):
    @mcp.tool()
    def create_kanban_board(
        columns: list[KanbanColumn],
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a Kanban board diagram.

        Generates a column-based task board with cards in each column.
        Great for visualizing workflows, sprints, and task status.

        Args:
            columns: List of columns with name and card labels
            title: Optional board title
            output_path: Optional output file path
            theme: Color theme - "light" or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        col_dicts = [
            {"name": c.name, "cards": c.cards, "color": c.color}
            for c in columns
        ]

        elements = create_kanban_elements(col_dicts, title=title)

        path = output_path or "/tmp/kanban.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Kanban board saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
