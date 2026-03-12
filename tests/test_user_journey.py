"""Tests for user journey map tool."""

import os
from excalidraw_mcp.tools.user_journey import create_journey_elements


def test_journey_basic():
    """Basic user journey with steps."""
    steps = [
        {"label": "Discover", "emotion": "happy", "description": "Find the product"},
        {"label": "Sign Up", "emotion": "neutral", "description": "Create account"},
        {"label": "First Use", "emotion": "happy", "description": "Try features"},
    ]
    elements = create_journey_elements(steps)
    assert len(elements) > 0

    # Should have shape elements for steps
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 3


def test_journey_emotions():
    """Emotions map to different colors."""
    steps = [
        {"label": "Step 1", "emotion": "happy"},
        {"label": "Step 2", "emotion": "sad"},
        {"label": "Step 3", "emotion": "neutral"},
    ]
    elements = create_journey_elements(steps)
    rects = [e for e in elements if e["type"] == "rectangle"]
    bgs = set(r.get("backgroundColor", "") for r in rects)
    assert len(bgs) >= 2  # at least happy and sad have different colors


def test_journey_with_title():
    """Journey with title."""
    steps = [{"label": "Step 1"}]
    elements = create_journey_elements(steps, title="Customer Journey")
    texts = [e for e in elements if e["type"] == "text"]
    title_texts = [t for t in texts if t.get("text") == "Customer Journey"]
    assert len(title_texts) == 1


def test_journey_save(tmp_path):
    """Journey map saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    steps = [
        {"label": "Aware", "emotion": "neutral"},
        {"label": "Consider", "emotion": "happy"},
    ]
    elements = create_journey_elements(steps, title="Buyer Journey")
    path = str(tmp_path / "journey.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
