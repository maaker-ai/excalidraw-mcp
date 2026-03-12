"""Tests for state diagram tool."""

import json
import os
from excalidraw_mcp.tools.state_diagram import create_state_elements


def test_state_basic():
    """Basic state diagram with transitions."""
    states = [
        {"name": "Idle"},
        {"name": "Running"},
        {"name": "Stopped"},
    ]
    transitions = [
        {"from": "Idle", "to": "Running", "label": "start"},
        {"from": "Running", "to": "Stopped", "label": "stop"},
    ]
    elements = create_state_elements(states, transitions)
    assert len(elements) > 0

    # States are rounded rectangles
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 3


def test_state_initial_final():
    """States with is_initial and is_final flags."""
    states = [
        {"name": "Start", "is_initial": True},
        {"name": "Process"},
        {"name": "End", "is_final": True},
    ]
    transitions = [
        {"from": "Start", "to": "Process", "label": "begin"},
        {"from": "Process", "to": "End", "label": "finish"},
    ]
    elements = create_state_elements(states, transitions)

    # Initial state should be an ellipse (small circle)
    ellipses = [e for e in elements if e["type"] == "ellipse"]
    assert len(ellipses) >= 1  # at least the initial marker


def test_state_self_transition():
    """Self-transition (state to itself)."""
    states = [{"name": "Active"}]
    transitions = [
        {"from": "Active", "to": "Active", "label": "retry"},
    ]
    elements = create_state_elements(states, transitions)
    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) >= 1


def test_state_save(tmp_path):
    """State diagram saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    states = [{"name": "On"}, {"name": "Off"}]
    transitions = [
        {"from": "On", "to": "Off", "label": "toggle"},
        {"from": "Off", "to": "On", "label": "toggle"},
    ]
    elements = create_state_elements(states, transitions)
    path = str(tmp_path / "state.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
