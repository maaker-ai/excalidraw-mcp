"""Table diagram tool — generates grid-based comparison tables."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width, create_centered_title
from ..elements.shapes import create_rectangle
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
CELL_PADDING = 15
ROW_HEIGHT = 36
HEADER_HEIGHT = 42
MIN_COL_WIDTH = 100
FONT_SIZE = 14
HEADER_FONT_SIZE = 15


def create_table_elements(
    headers: list[str],
    rows: list[list[str]],
    title: Optional[str] = None,
    header_color: str = "blue",
) -> list[dict]:
    """Create table elements.

    Args:
        headers: List of column header strings
        rows: List of row data (each row is a list of cell strings)
        title: Optional table title
        header_color: Color for header row

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    num_cols = len(headers)
    color = get_color(header_color)

    # Calculate column widths based on content
    col_widths = []
    for col_idx in range(num_cols):
        max_width = estimate_text_width(headers[col_idx], HEADER_FONT_SIZE) + CELL_PADDING * 2
        for row in rows:
            if col_idx < len(row):
                cell_width = estimate_text_width(row[col_idx], FONT_SIZE) + CELL_PADDING * 2
                max_width = max(max_width, cell_width)
        col_widths.append(max(max_width, MIN_COL_WIDTH))

    # Draw header row
    x = 0
    for col_idx, header in enumerate(headers):
        cw = col_widths[col_idx]
        cell = create_rectangle(
            gen_id(), x, 0, cw, HEADER_HEIGHT,
            background_color=color["bg"],
            stroke_color=color["stroke"],
        )
        elements.append(cell)

        text = create_text(
            gen_id(), header,
            x=x + (cw - estimate_text_width(header, HEADER_FONT_SIZE)) / 2,
            y=(HEADER_HEIGHT - HEADER_FONT_SIZE * 1.4) / 2,
            font_size=HEADER_FONT_SIZE,
            width=estimate_text_width(header, HEADER_FONT_SIZE),
            height=HEADER_FONT_SIZE * 1.4,
        )
        elements.append(text)
        x += cw

    # Draw data rows
    for row_idx, row in enumerate(rows):
        y = HEADER_HEIGHT + row_idx * ROW_HEIGHT
        x = 0
        bg = "#ffffff" if row_idx % 2 == 0 else "#f8f9fa"
        for col_idx in range(num_cols):
            cw = col_widths[col_idx]
            cell_text = row[col_idx] if col_idx < len(row) else ""

            cell = create_rectangle(
                gen_id(), x, y, cw, ROW_HEIGHT,
                background_color=bg,
                stroke_color="#dee2e6",
                strokeWidth=1,
            )
            elements.append(cell)

            if cell_text:
                text = create_text(
                    gen_id(), cell_text,
                    x=x + (cw - estimate_text_width(cell_text, FONT_SIZE)) / 2,
                    y=y + (ROW_HEIGHT - FONT_SIZE * 1.4) / 2,
                    font_size=FONT_SIZE,
                    width=estimate_text_width(cell_text, FONT_SIZE),
                    height=FONT_SIZE * 1.4,
                )
                elements.append(text)
            x += cw

    # Title
    if title:
        elements.insert(0, create_centered_title(title, elements))

    return elements


class TableRow(BaseModel):
    cells: list[str] = Field(description="List of cell values for this row")


def register_table_tools(mcp: FastMCP):
    @mcp.tool()
    def create_table(
        headers: list[str],
        rows: list[list[str]],
        title: Optional[str] = None,
        header_color: str = "blue",
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a table diagram.

        Generates a grid-based table with header row and data rows.
        Auto-sizes columns based on content. Great for comparison tables,
        feature matrices, and data displays.

        Args:
            headers: Column header labels
            rows: List of rows, each row is a list of cell values
            title: Optional table title
            header_color: Header row color name
            output_path: Optional output file path
            theme: Color theme

        Returns:
            Absolute path to the generated .excalidraw file
        """
        elements = create_table_elements(headers, rows, title=title, header_color=header_color)

        path = output_path or "/tmp/table.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Table saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
