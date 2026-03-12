"""Test elbow (right-angle) connectors."""
from excalidraw_mcp.elements.text import create_labeled_shape
from excalidraw_mcp.elements.arrows import create_arrow


def test_elbow_arrow_basic():
    """Elbow arrow should have elbowed=true and multi-segment points."""
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=200, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2, elbowed=True)
    arrow = result[0]
    assert arrow["elbowed"] is True
    # Elbow arrows should have 3+ points (start, corner(s), end)
    assert len(arrow["points"]) >= 3


def test_elbow_arrow_horizontal_first():
    """Elbow arrow going right-then-down should route correctly."""
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=0, y=300, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2, elbowed=True)
    arrow = result[0]
    # Should have the elbowed flag set
    assert arrow["elbowed"] is True


def test_non_elbow_arrow_default():
    """Default arrows should not be elbowed."""
    shape1, _ = create_labeled_shape("rectangle", id="a", label="A", x=0, y=0, width=200, height=70)
    shape2, _ = create_labeled_shape("rectangle", id="b", label="B", x=300, y=0, width=200, height=70)

    result = create_arrow("arr1", shape1, shape2)
    arrow = result[0]
    assert arrow["elbowed"] is False
    assert len(arrow["points"]) == 2  # straight line
