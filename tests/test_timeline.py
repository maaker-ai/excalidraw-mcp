"""Tests for timeline diagram tool."""

import json
import os
from excalidraw_mcp.tools.timeline import create_timeline_elements


def test_timeline_basic():
    """Basic timeline with events creates elements."""
    events = [
        {"label": "Phase 1", "start": 0, "end": 3},
        {"label": "Phase 2", "start": 3, "end": 6},
        {"label": "Phase 3", "start": 6, "end": 9},
    ]
    elements = create_timeline_elements(events)
    assert len(elements) > 0

    # Should have rectangles for timeline bars
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 3  # one bar per event

    # Should have text labels
    texts = [e for e in elements if e["type"] == "text"]
    assert len(texts) >= 3


def test_timeline_overlapping():
    """Overlapping events should be on different rows."""
    events = [
        {"label": "Task A", "start": 0, "end": 5},
        {"label": "Task B", "start": 2, "end": 7},
        {"label": "Task C", "start": 6, "end": 9},
    ]
    elements = create_timeline_elements(events)

    rects = [e for e in elements if e["type"] == "rectangle"]
    # Task A and B overlap, so they should have different y positions
    bar_ys = sorted(set(r["y"] for r in rects))
    assert len(bar_ys) >= 2  # at least 2 rows since A and B overlap


def test_timeline_with_title():
    """Timeline with title includes title text."""
    events = [
        {"label": "Start", "start": 0, "end": 2},
    ]
    elements = create_timeline_elements(events, title="Project Timeline")
    texts = [e for e in elements if e["type"] == "text"]
    title_texts = [t for t in texts if t.get("text") == "Project Timeline"]
    assert len(title_texts) == 1


def test_timeline_colors():
    """Events with colors use correct fill."""
    events = [
        {"label": "Dev", "start": 0, "end": 5, "color": "blue"},
        {"label": "Test", "start": 5, "end": 8, "color": "green"},
    ]
    elements = create_timeline_elements(events)
    rects = [e for e in elements if e["type"] == "rectangle"]
    # Different colors should result in different backgrounds
    bgs = set(r.get("backgroundColor", "") for r in rects)
    assert len(bgs) >= 2


def test_timeline_save(tmp_path):
    """Timeline saves to file correctly."""
    from excalidraw_mcp.tools.timeline import create_timeline_elements
    from excalidraw_mcp.utils.file_io import save_excalidraw

    events = [
        {"label": "Alpha", "start": 0, "end": 3},
        {"label": "Beta", "start": 3, "end": 6},
    ]
    elements = create_timeline_elements(events, title="Release Plan")
    path = str(tmp_path / "timeline.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
    with open(result) as f:
        data = json.load(f)
    assert len(data["elements"]) > 0
