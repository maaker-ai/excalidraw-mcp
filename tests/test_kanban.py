"""Tests for kanban board tool."""

import json
import os
from excalidraw_mcp.tools.kanban import create_kanban_elements


def test_kanban_basic():
    """Basic kanban with columns and cards."""
    columns = [
        {"name": "To Do", "cards": ["Task 1", "Task 2"]},
        {"name": "In Progress", "cards": ["Task 3"]},
        {"name": "Done", "cards": ["Task 4"]},
    ]
    elements = create_kanban_elements(columns)
    assert len(elements) > 0

    # Should have rectangles for columns and cards
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 7  # 3 column backgrounds + 4 cards


def test_kanban_column_colors():
    """Columns can have custom colors."""
    columns = [
        {"name": "Backlog", "cards": ["A"], "color": "gray"},
        {"name": "Active", "cards": ["B"], "color": "blue"},
        {"name": "Done", "cards": ["C"], "color": "green"},
    ]
    elements = create_kanban_elements(columns)
    rects = [e for e in elements if e["type"] == "rectangle"]
    # Different bg colors
    bgs = set(r.get("backgroundColor", "") for r in rects)
    assert len(bgs) >= 2


def test_kanban_empty_column():
    """Empty column still renders."""
    columns = [
        {"name": "Empty", "cards": []},
        {"name": "Has Cards", "cards": ["X"]},
    ]
    elements = create_kanban_elements(columns)
    assert len(elements) > 0


def test_kanban_save(tmp_path):
    """Kanban saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    columns = [
        {"name": "Todo", "cards": ["Write tests"]},
    ]
    elements = create_kanban_elements(columns, title="Sprint Board")
    path = str(tmp_path / "kanban.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
