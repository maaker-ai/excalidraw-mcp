"""简单 SVG 导出：将 .excalidraw JSON 转换为基础 SVG。

不追求手绘风格，只需几何图形可读即可。
支持：rectangle, ellipse, diamond, text, arrow/line。
"""

import html
from typing import Optional


def _compute_viewbox(elements: list[dict], padding: int = 20) -> tuple[float, float, float, float]:
    """计算所有元素的 bounding box，返回 (min_x, min_y, width, height)"""
    if not elements:
        return (0, 0, 800, 600)

    xs = []
    ys = []
    for el in elements:
        if el.get("isDeleted"):
            continue
        x = el.get("x", 0)
        y = el.get("y", 0)
        w = el.get("width", 0)
        h = el.get("height", 0)
        xs.extend([x, x + w])
        ys.extend([y, y + h])

    if not xs:
        return (0, 0, 800, 600)

    min_x = min(xs) - padding
    min_y = min(ys) - padding
    max_x = max(xs) + padding
    max_y = max(ys) + padding
    return (min_x, min_y, max_x - min_x, max_y - min_y)


def _opacity_to_pct(opacity: int) -> float:
    return opacity / 100.0


def _render_rectangle(el: dict) -> str:
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 100)
    h = el.get("height", 60)
    fill = el.get("backgroundColor", "#a5d8ff")
    stroke = el.get("strokeColor", "#1e1e1e")
    stroke_w = el.get("strokeWidth", 2)
    opacity = _opacity_to_pct(el.get("opacity", 100))
    roundness = el.get("roundness")
    rx = 8 if roundness else 0

    if fill in ("transparent", "none", ""):
        fill = "none"

    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" opacity="{opacity}" />'
    )


def _render_ellipse(el: dict) -> str:
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 100)
    h = el.get("height", 60)
    cx = x + w / 2
    cy = y + h / 2
    rx = w / 2
    ry = h / 2
    fill = el.get("backgroundColor", "#ffec99")
    stroke = el.get("strokeColor", "#1e1e1e")
    stroke_w = el.get("strokeWidth", 2)
    opacity = _opacity_to_pct(el.get("opacity", 100))

    if fill in ("transparent", "none", ""):
        fill = "none"

    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" opacity="{opacity}" />'
    )


def _render_diamond(el: dict) -> str:
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 100)
    h = el.get("height", 60)
    # 菱形四个顶点
    points = f"{x + w/2},{y} {x + w},{y + h/2} {x + w/2},{y + h} {x},{y + h/2}"
    fill = el.get("backgroundColor", "#ffc9c9")
    stroke = el.get("strokeColor", "#1e1e1e")
    stroke_w = el.get("strokeWidth", 2)
    opacity = _opacity_to_pct(el.get("opacity", 100))

    if fill in ("transparent", "none", ""):
        fill = "none"

    return (
        f'<polygon points="{points}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" opacity="{opacity}" />'
    )


def _render_text(el: dict) -> str:
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 100)
    h = el.get("height", 28)
    font_size = el.get("fontSize", 20)
    color = el.get("strokeColor", "#1e1e1e")
    text_align = el.get("textAlign", "left")
    opacity = _opacity_to_pct(el.get("opacity", 100))
    raw_text = el.get("text", "")

    # SVG text anchor
    anchor_map = {"left": "start", "center": "middle", "right": "end"}
    anchor = anchor_map.get(text_align, "start")

    # x 坐标根据对齐方式调整
    if text_align == "center":
        tx = x + w / 2
    elif text_align == "right":
        tx = x + w
    else:
        tx = x

    # 垂直居中：基于 y + height/2
    ty = y + h / 2 + font_size * 0.35

    lines = raw_text.split("\n")
    if len(lines) == 1:
        escaped = html.escape(raw_text)
        return (
            f'<text x="{tx}" y="{ty}" font-size="{font_size}" fill="{color}" '
            f'text-anchor="{anchor}" opacity="{opacity}" font-family="Arial, sans-serif">'
            f'{escaped}</text>'
        )
    else:
        line_height = font_size * 1.4
        parts = []
        for i, line in enumerate(lines):
            dy = 0 if i == 0 else line_height
            escaped = html.escape(line)
            parts.append(f'<tspan x="{tx}" dy="{dy}">{escaped}</tspan>')
        inner = "".join(parts)
        return (
            f'<text x="{tx}" y="{ty}" font-size="{font_size}" fill="{color}" '
            f'text-anchor="{anchor}" opacity="{opacity}" font-family="Arial, sans-serif">'
            f'{inner}</text>'
        )


def _render_arrow(el: dict) -> str:
    """渲染箭头/线条为 SVG path"""
    ax = el.get("x", 0)
    ay = el.get("y", 0)
    points = el.get("points", [[0, 0], [50, 0]])
    stroke = el.get("strokeColor", "#1e1e1e")
    stroke_w = el.get("strokeWidth", 2)
    opacity = _opacity_to_pct(el.get("opacity", 100))
    end_arrowhead = el.get("endArrowhead", "arrow")
    start_arrowhead = el.get("startArrowhead", None)
    stroke_style = el.get("strokeStyle", "solid")

    # 转换为全局坐标
    global_pts = [(ax + p[0], ay + p[1]) for p in points]

    if len(global_pts) < 2:
        return ""

    # 构建路径
    path_d = f"M {global_pts[0][0]} {global_pts[0][1]}"
    for pt in global_pts[1:]:
        path_d += f" L {pt[0]} {pt[1]}"

    dash = 'stroke-dasharray="8,4"' if stroke_style == "dashed" else ""
    dot = 'stroke-dasharray="2,4"' if stroke_style == "dotted" else ""
    dash_attr = dash or dot

    # 箭头标记 id（基于元素 id）
    el_id = el.get("id", "arrow")
    marker_end = ""
    marker_start = ""
    marker_defs = ""

    if end_arrowhead == "arrow":
        marker_id = f"arrowhead-end-{el_id}"
        marker_defs += (
            f'<defs><marker id="{marker_id}" markerWidth="10" markerHeight="7" '
            f'refX="9" refY="3.5" orient="auto">'
            f'<polygon points="0 0, 10 3.5, 0 7" fill="{stroke}" /></marker></defs>'
        )
        marker_end = f'marker-end="url(#{marker_id})"'

    if start_arrowhead == "arrow":
        marker_id_s = f"arrowhead-start-{el_id}"
        marker_defs += (
            f'<defs><marker id="{marker_id_s}" markerWidth="10" markerHeight="7" '
            f'refX="1" refY="3.5" orient="auto-start-reverse">'
            f'<polygon points="0 0, 10 3.5, 0 7" fill="{stroke}" /></marker></defs>'
        )
        marker_start = f'marker-start="url(#{marker_id_s})"'

    return (
        f'{marker_defs}'
        f'<path d="{path_d}" fill="none" stroke="{stroke}" stroke-width="{stroke_w}" '
        f'opacity="{opacity}" {dash_attr} {marker_end} {marker_start} />'
    )


def export_to_svg(excalidraw_data: dict) -> str:
    """将 excalidraw JSON 转成 SVG 字符串"""
    elements = excalidraw_data.get("elements", [])
    bg_color = excalidraw_data.get("appState", {}).get("viewBackgroundColor", "#ffffff")

    # 过滤已删除元素
    visible = [el for el in elements if not el.get("isDeleted", False)]

    min_x, min_y, vw, vh = _compute_viewbox(visible)

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x} {min_y} {vw} {vh}" '
        f'width="{vw}" height="{vh}">',
        f'<rect x="{min_x}" y="{min_y}" width="{vw}" height="{vh}" fill="{bg_color}" />',
    ]

    # 渲染顺序：先形状，后文字，最后箭头（确保箭头在最上层）
    shape_parts = []
    text_parts = []
    arrow_parts = []

    for el in visible:
        el_type = el.get("type", "")
        if el_type == "rectangle":
            shape_parts.append(_render_rectangle(el))
        elif el_type == "ellipse":
            shape_parts.append(_render_ellipse(el))
        elif el_type == "diamond":
            shape_parts.append(_render_diamond(el))
        elif el_type == "text":
            text_parts.append(_render_text(el))
        elif el_type in ("arrow", "line"):
            arrow_parts.append(_render_arrow(el))
        # 其他类型暂不渲染

    svg_parts.extend(shape_parts)
    svg_parts.extend(text_parts)
    svg_parts.extend(arrow_parts)
    svg_parts.append("</svg>")

    return "\n".join(svg_parts)
