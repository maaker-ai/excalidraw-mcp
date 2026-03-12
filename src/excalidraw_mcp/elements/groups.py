"""Group frame elements — background rectangles that visually contain related nodes."""

from ..utils.ids import gen_id
from .shapes import create_rectangle
from .text import create_text, estimate_text_width
from .style import get_color

# Padding around the group of nodes
GROUP_PADDING = 30
# Space above for the group label
LABEL_HEIGHT = 30
LABEL_FONT_SIZE = 16


def create_group_frame(
    name: str,
    node_bounds: list[dict],
    color: str = "gray",
) -> list[dict]:
    """Create a frame rectangle + label that visually groups nodes.

    Args:
        name: Group label text
        node_bounds: List of dicts with x, y, width, height for each node in the group
        color: Color name for the frame stroke

    Returns:
        [frame_rect, label_text] — insert at beginning of elements list so they render behind nodes
    """
    if not node_bounds:
        return []

    # Compute bounding box of all nodes
    min_x = min(b["x"] for b in node_bounds)
    min_y = min(b["y"] for b in node_bounds)
    max_x = max(b["x"] + b["width"] for b in node_bounds)
    max_y = max(b["y"] + b["height"] for b in node_bounds)

    # Frame with padding + label space
    frame_x = min_x - GROUP_PADDING
    frame_y = min_y - GROUP_PADDING - LABEL_HEIGHT
    frame_w = (max_x - min_x) + 2 * GROUP_PADDING
    frame_h = (max_y - min_y) + 2 * GROUP_PADDING + LABEL_HEIGHT

    c = get_color(color)
    frame_id = gen_id()

    frame_rect = create_rectangle(
        frame_id,
        frame_x, frame_y, frame_w, frame_h,
        background_color="transparent",
        stroke_color=c["stroke"],
        strokeStyle="dashed",
        strokeWidth=1,
        roughness=0,
        opacity=60,
    )

    # Label text at top-left of frame
    label_id = gen_id()
    label_width = estimate_text_width(name, LABEL_FONT_SIZE)
    label_text = create_text(
        label_id, name,
        x=frame_x + 10,
        y=frame_y + 8,
        font_size=LABEL_FONT_SIZE,
        width=label_width,
        height=LABEL_FONT_SIZE * 1.4,
        strokeColor=c["stroke"],
        opacity=70,
    )

    return [frame_rect, label_text]
