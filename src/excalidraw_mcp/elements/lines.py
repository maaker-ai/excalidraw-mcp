"""Line element creation utility."""

import random
import time

from ..utils.ids import gen_id


def create_line(
    x1: float, y1: float, x2: float, y2: float,
    stroke_color: str = "#1e1e1e",
    stroke_width: int = 2,
    stroke_style: str = "solid",
) -> dict:
    """Create a line element from (x1, y1) to (x2, y2).

    Args:
        x1, y1: Start point
        x2, y2: End point
        stroke_color: Line color
        stroke_width: Line thickness
        stroke_style: "solid", "dashed", or "dotted"

    Returns:
        Excalidraw line element dict
    """
    return {
        "id": gen_id(),
        "type": "line",
        "x": x1,
        "y": y1,
        "width": abs(x2 - x1) or 1,
        "height": abs(y2 - y1) or 1,
        "strokeColor": stroke_color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "strokeStyle": stroke_style,
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": random.randint(1, 2**31),
        "version": 1,
        "versionNonce": random.randint(1, 2**31),
        "isDeleted": False,
        "groupIds": [],
        "boundElements": [],
        "updated": int(time.time() * 1000),
        "link": None,
        "locked": False,
        "roundness": None,
        "points": [[0, 0], [x2 - x1, y2 - y1]],
        "lastCommittedPoint": None,
        "startArrowhead": None,
        "endArrowhead": None,
        "startBinding": None,
        "endBinding": None,
    }
