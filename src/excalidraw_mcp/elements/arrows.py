import random
import time
from typing import Optional


# fixedPoint 映射：side -> [x, y] 归一化坐标
_FIXED_POINTS = {
    "right":  [1.0,    0.5001],
    "left":   [0.0,    0.5001],
    "bottom": [0.5001, 1.0],
    "top":    [0.5001, 0.0],
}


def _center(el: dict) -> tuple:
    return (el["x"] + el["width"] / 2, el["y"] + el["height"] / 2)


def _edge_point(el: dict, side: str) -> tuple:
    """返回形状某条边中心点的全局坐标"""
    x, y, w, h = el["x"], el["y"], el["width"], el["height"]
    if side == "right":
        return (x + w, y + h / 2)
    elif side == "left":
        return (x, y + h / 2)
    elif side == "bottom":
        return (x + w / 2, y + h)
    elif side == "top":
        return (x + w / 2, y)
    else:
        raise ValueError(f"未知边: {side}")


def _auto_sides(start_el: dict, end_el: dict) -> tuple:
    """根据两个形状相对位置自动判断连接边"""
    sx, sy = _center(start_el)
    ex, ey = _center(end_el)
    dx = abs(ex - sx)
    dy = abs(ey - sy)

    if dx >= dy:
        # 水平连接
        if ex > sx:
            return ("right", "left")
        else:
            return ("left", "right")
    else:
        # 垂直连接
        if ey > sy:
            return ("bottom", "top")
        else:
            return ("top", "bottom")


from ..utils.ids import gen_id as _gen_id


def create_arrow(id: str, start_element: dict, end_element: dict,
                 start_side: str = "auto", end_side: str = "auto",
                 label: Optional[str] = None, **kwargs) -> list:
    """创建箭头元素，连接两个形状。

    start_element, end_element: 形状 dict（需要 id, x, y, width, height）
    start_side, end_side: "left"|"right"|"top"|"bottom"|"auto"
    label: 可选的边标签文字

    auto 模式根据两个形状的相对位置判断连接边。

    关键规范：
    - startBinding/endBinding 用 fixedPoint + mode="orbit"
    - arrow.x, arrow.y = 起点在框边缘的全局坐标
    - points = [[0,0], [dx, dy]] 相对偏移
    - 不使用废弃的 focus/gap 格式

    返回值：list[dict]
    - 无标签: [arrow]
    - 有标签: [arrow, text]
    """
    if id is None:
        id = "arrow_" + _gen_id()

    # 自动判断连接边
    if start_side == "auto" or end_side == "auto":
        auto_start, auto_end = _auto_sides(start_element, end_element)
        if start_side == "auto":
            start_side = auto_start
        if end_side == "auto":
            end_side = auto_end

    # 计算起点和终点的全局坐标（形状边缘中心）
    start_x, start_y = _edge_point(start_element, start_side)
    end_x, end_y = _edge_point(end_element, end_side)

    # arrow.x/y = 起点；points 为相对偏移
    arrow_x = start_x
    arrow_y = start_y
    rel_dx = end_x - start_x
    rel_dy = end_y - start_y

    # Elbow routing: compute right-angle path
    is_elbowed = kwargs.get("elbowed", False)
    if is_elbowed and abs(rel_dx) > 1 and abs(rel_dy) > 1:
        # Route with a midpoint for right-angle turn
        if start_side in ("right", "left"):
            # Go horizontal first, then vertical
            mid_x = rel_dx / 2
            points = [[0, 0], [mid_x, 0], [mid_x, rel_dy], [rel_dx, rel_dy]]
        else:
            # Go vertical first, then horizontal
            mid_y = rel_dy / 2
            points = [[0, 0], [0, mid_y], [rel_dx, mid_y], [rel_dx, rel_dy]]
    else:
        points = [[0, 0], [rel_dx, rel_dy]]

    start_fixed = _FIXED_POINTS[start_side]
    end_fixed = _FIXED_POINTS[end_side]

    arrow = {
        "id": id,
        "type": "arrow",
        "x": arrow_x,
        "y": arrow_y,
        "width": abs(rel_dx),
        "height": abs(rel_dy),
        "strokeColor": kwargs.get("strokeColor", "#1e1e1e"),
        "backgroundColor": kwargs.get("backgroundColor", "transparent"),
        "fillStyle": kwargs.get("fillStyle", "solid"),
        "strokeWidth": kwargs.get("strokeWidth", 2),
        "strokeStyle": kwargs.get("strokeStyle", "solid"),
        "roughness": kwargs.get("roughness", 1),
        "opacity": kwargs.get("opacity", 100),
        "angle": kwargs.get("angle", 0),
        "seed": kwargs.get("seed", random.randint(1, 2**31)),
        "version": kwargs.get("version", 1),
        "versionNonce": kwargs.get("versionNonce", random.randint(1, 2**31)),
        "isDeleted": False,
        "groupIds": kwargs.get("groupIds", []),
        "boundElements": [],
        "updated": kwargs.get("updated", int(time.time() * 1000)),
        "link": None,
        "locked": False,
        "roundness": {"type": 2},
        "points": points,
        "lastCommittedPoint": None,
        "startArrowhead": kwargs.get("startArrowhead", None),
        "endArrowhead": kwargs.get("endArrowhead", "arrow"),
        "startBinding": {
            "elementId": start_element["id"],
            "fixedPoint": start_fixed,
            "mode": "orbit",
        },
        "endBinding": {
            "elementId": end_element["id"],
            "fixedPoint": end_fixed,
            "mode": "orbit",
        },
        "elbowed": kwargs.get("elbowed", False),
    }

    # 如果有标签，创建绑定文字元素
    if label:
        from .text import create_text, estimate_text_width
        text_id = id + "_label"
        font_size = 16
        text_width = estimate_text_width(label, font_size)
        text_height = font_size * 1.4

        # 文字位于箭头中点
        mid_x = arrow_x + rel_dx / 2
        mid_y = arrow_y + rel_dy / 2
        text_x = mid_x - text_width / 2
        text_y = mid_y - text_height / 2

        text_elem = create_text(
            text_id, label, text_x, text_y,
            font_size=font_size,
            container_id=id,
            width=text_width,
            height=text_height,
        )
        arrow["boundElements"].append({"id": text_id, "type": "text"})

    # 更新 start_element 和 end_element 的 boundElements
    arrow_ref = {"id": id, "type": "arrow"}
    if arrow_ref not in start_element.get("boundElements", []):
        start_element.setdefault("boundElements", []).append(arrow_ref)
    if arrow_ref not in end_element.get("boundElements", []):
        end_element.setdefault("boundElements", []).append(arrow_ref)

    if label:
        return [arrow, text_elem]
    return [arrow]
