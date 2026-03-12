"""Tests for table diagram tool."""

import os
from excalidraw_mcp.tools.table import create_table_elements


def test_table_basic():
    """Basic table with headers and rows."""
    headers = ["Name", "Type", "Status"]
    rows = [
        ["Alice", "Admin", "Active"],
        ["Bob", "User", "Inactive"],
    ]
    elements = create_table_elements(headers, rows)
    assert len(elements) > 0

    rects = [e for e in elements if e["type"] == "rectangle"]
    # Header row cells + data row cells = 3 + 6 = 9
    assert len(rects) >= 9


def test_table_with_title():
    """Table with title."""
    headers = ["A", "B"]
    rows = [["1", "2"]]
    elements = create_table_elements(headers, rows, title="My Table")
    texts = [e for e in elements if e["type"] == "text"]
    assert any(t["text"] == "My Table" for t in texts)


def test_table_save(tmp_path):
    """Table saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    headers = ["Col1"]
    rows = [["Val1"]]
    elements = create_table_elements(headers, rows)
    path = str(tmp_path / "table.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
