"""Test Mermaid sequence diagram import."""


def test_parse_mermaid_sequence_basic():
    """Parse basic Mermaid sequence diagram syntax."""
    from excalidraw_mcp.tools.mermaid import parse_mermaid_sequence

    mermaid = """sequenceDiagram
    Alice->>Bob: Hello
    Bob-->>Alice: Hi"""

    participants, messages = parse_mermaid_sequence(mermaid)
    assert "Alice" in participants
    assert "Bob" in participants
    assert len(messages) == 2
    assert messages[0]["from"] == "Alice"
    assert messages[0]["to"] == "Bob"
    assert messages[0]["label"] == "Hello"
    assert messages[1]["style"] == "dashed"  # -->> is return/dashed


def test_parse_mermaid_sequence_explicit_participants():
    """Parse explicit participant declarations."""
    from excalidraw_mcp.tools.mermaid import parse_mermaid_sequence

    mermaid = """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Message"""

    participants, messages = parse_mermaid_sequence(mermaid)
    assert "Alice" in participants
    assert "Bob" in participants
    assert messages[0]["from"] == "Alice"
    assert messages[0]["to"] == "Bob"


def test_parse_mermaid_sequence_self_message():
    """Parse self-message in sequence diagram."""
    from excalidraw_mcp.tools.mermaid import parse_mermaid_sequence

    mermaid = """sequenceDiagram
    A->>A: Think"""

    participants, messages = parse_mermaid_sequence(mermaid)
    assert len(messages) == 1
    assert messages[0]["from"] == "A"
    assert messages[0]["to"] == "A"
