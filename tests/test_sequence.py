"""Test sequence diagram generation."""
import json
import os
import tempfile


def test_sequence_diagram_basic():
    """Basic sequence diagram with 3 participants and 2 messages."""
    from excalidraw_mcp.tools.sequence import create_sequence_elements

    participants = ["Client", "Server", "Database"]
    messages = [
        {"from": "Client", "to": "Server", "label": "HTTP Request"},
        {"from": "Server", "to": "Database", "label": "SQL Query"},
    ]

    elements = create_sequence_elements(participants, messages)
    assert len(elements) > 0

    # Should have participant rectangles
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 3  # at least 3 participant boxes

    # Should have arrows for messages
    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) == 2

    # Should have text labels
    texts = [e for e in elements if e["type"] == "text"]
    text_values = [t["text"] for t in texts]
    assert "Client" in text_values
    assert "Server" in text_values
    assert "Database" in text_values
    assert "HTTP Request" in text_values
    assert "SQL Query" in text_values


def test_sequence_diagram_lifelines():
    """Sequence diagram should have vertical dashed lifelines."""
    from excalidraw_mcp.tools.sequence import create_sequence_elements

    participants = ["A", "B"]
    messages = [{"from": "A", "to": "B", "label": "msg"}]

    elements = create_sequence_elements(participants, messages)

    # Lifelines are line elements with dashed style
    lines = [e for e in elements if e["type"] == "line"]
    assert len(lines) == 2  # one per participant

    for line in lines:
        assert line["strokeStyle"] == "dashed"
        # Lifelines should be vertical (same x for start and end)
        assert line["points"][1][0] == 0  # dx = 0


def test_sequence_diagram_self_message():
    """Self-message (same source and target) should work."""
    from excalidraw_mcp.tools.sequence import create_sequence_elements

    participants = ["A", "B"]
    messages = [{"from": "A", "to": "A", "label": "self call"}]

    elements = create_sequence_elements(participants, messages)
    # Should not crash, should have at least the self-message arrow
    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) >= 1


def test_sequence_diagram_return_message():
    """Dashed return messages should have dashed style."""
    from excalidraw_mcp.tools.sequence import create_sequence_elements

    participants = ["A", "B"]
    messages = [
        {"from": "A", "to": "B", "label": "request"},
        {"from": "B", "to": "A", "label": "response", "style": "dashed"},
    ]

    elements = create_sequence_elements(participants, messages)
    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) == 2
    # Second arrow should be dashed
    dashed_arrows = [a for a in arrows if a["strokeStyle"] == "dashed"]
    assert len(dashed_arrows) >= 1


def test_sequence_diagram_save():
    """Sequence diagram should save to a valid .excalidraw file."""
    from excalidraw_mcp.tools.sequence import create_sequence_elements
    from excalidraw_mcp.utils.file_io import save_excalidraw, load_excalidraw

    participants = ["User", "API", "DB"]
    messages = [
        {"from": "User", "to": "API", "label": "GET /users"},
        {"from": "API", "to": "DB", "label": "SELECT *"},
        {"from": "DB", "to": "API", "label": "rows", "style": "dashed"},
        {"from": "API", "to": "User", "label": "200 OK", "style": "dashed"},
    ]

    elements = create_sequence_elements(participants, messages)

    with tempfile.NamedTemporaryFile(suffix=".excalidraw", delete=False) as f:
        path = f.name

    try:
        save_excalidraw(elements, path)
        data = load_excalidraw(path)
        assert data["type"] == "excalidraw"
        assert len(data["elements"]) > 0
    finally:
        os.unlink(path)
