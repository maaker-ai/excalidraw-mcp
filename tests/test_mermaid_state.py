"""Tests for Mermaid state diagram parsing."""

from excalidraw_mcp.tools.mermaid import parse_mermaid_state


def test_parse_state_basic():
    """Parse basic state transitions."""
    text = """stateDiagram-v2
    [*] --> Idle
    Idle --> Running : start
    Running --> Stopped : stop
    Stopped --> [*]
    """
    states, transitions = parse_mermaid_state(text)
    assert len(states) >= 3  # Idle, Running, Stopped
    assert len(transitions) >= 2  # [*] transitions become initial/final markers, not transitions


def test_parse_state_self_transition():
    """Parse self-transition."""
    text = """stateDiagram-v2
    Active --> Active : retry
    """
    states, transitions = parse_mermaid_state(text)
    assert any(t["from"] == "Active" and t["to"] == "Active" for t in transitions)


def test_parse_state_initial_final():
    """Parse [*] as initial/final markers."""
    text = """stateDiagram-v2
    [*] --> Start
    End --> [*]
    """
    states, transitions = parse_mermaid_state(text)
    # Start should be marked as initial
    start_state = next((s for s in states if s["name"] == "Start"), None)
    assert start_state is not None
    assert start_state.get("is_initial") is True
