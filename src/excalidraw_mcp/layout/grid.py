from typing import Optional

from ..elements.text import estimate_text_width


def grid_layout(
    nodes: list[dict],
    direction: str = "horizontal",
    col_gap: int = 100,
    row_gap: int = 90,
    box_height: int = 70,
    columns: int = 3,
) -> list[dict]:
    """计算网格布局坐标。

    nodes: [{label: str, color?: str, width?: int, ...}]
    direction: "horizontal"（行优先）或 "vertical"（列优先）
    columns: 水平模式下每行列数（默认 3）

    返回带 x, y, width, height 字段的节点列表（原 dict 的副本）。

    算法：
    1. 对每个节点估算文字宽度，计算 box_width = max(text_width + 60, 200)
    2. 按 direction 排列成网格
    3. 每列宽度 = 该列最大 box_width
    4. x = sum(前面列宽度) + sum(前面 col_gap)
    5. y = row_index * (box_height + row_gap)
    """
    n = len(nodes)
    if n == 0:
        return []

    result = []

    if direction == "horizontal":
        num_cols = columns
        num_rows = (n + num_cols - 1) // num_cols

        # 计算每个节点的 box_width
        box_widths = []
        for node in nodes:
            if node.get("width"):
                box_widths.append(node["width"])
            else:
                tw = estimate_text_width(node.get("label", ""), font_size=20)
                box_widths.append(max(tw + 60, 200))

        # 每列最大宽度
        col_widths = []
        for col in range(num_cols):
            max_w = 0
            for row in range(num_rows):
                idx = row * num_cols + col
                if idx < n:
                    max_w = max(max_w, box_widths[idx])
            col_widths.append(max_w)

        # 每列起始 x 坐标
        col_x_starts = []
        cx = 0
        for col in range(num_cols):
            col_x_starts.append(cx)
            cx += col_widths[col] + col_gap

        for idx, node in enumerate(nodes):
            row = idx // num_cols
            col = idx % num_cols
            node_copy = dict(node)
            node_copy["x"] = col_x_starts[col]
            node_copy["y"] = row * (box_height + row_gap)
            node_copy["width"] = box_widths[idx]
            node_copy["height"] = box_height
            result.append(node_copy)

    elif direction == "vertical":
        # 列优先：从上到下排，填满后开新列
        num_rows = (n + columns - 1) // columns if columns else n
        # 列优先时默认每列行数 = ceil(n / columns)
        # 简化为每列 num_rows 行
        num_cols_actual = (n + num_rows - 1) // num_rows

        # 计算每个节点的 box_width
        box_widths = []
        for node in nodes:
            if node.get("width"):
                box_widths.append(node["width"])
            else:
                tw = estimate_text_width(node.get("label", ""), font_size=20)
                box_widths.append(max(tw + 60, 200))

        # 每列最大宽度
        col_widths = [0] * num_cols_actual
        for idx in range(n):
            col = idx // num_rows
            col_widths[col] = max(col_widths[col], box_widths[idx])

        # 每列起始 x
        col_x_starts = []
        cx = 0
        for col in range(num_cols_actual):
            col_x_starts.append(cx)
            cx += col_widths[col] + col_gap

        for idx, node in enumerate(nodes):
            col = idx // num_rows
            row = idx % num_rows
            node_copy = dict(node)
            node_copy["x"] = col_x_starts[col]
            node_copy["y"] = row * (box_height + row_gap)
            node_copy["width"] = box_widths[idx]
            node_copy["height"] = box_height
            result.append(node_copy)

    else:
        raise ValueError(f"不支持的 direction: {direction}，请使用 horizontal 或 vertical")

    return result


def layered_layout(
    layers: list[dict],
    layer_gap: int = 120,
    component_gap: int = 40,
    box_height: int = 70,
) -> list[dict]:
    """分层布局（用于架构图）。

    layers: [{name: str, components: [{label: str, color?: str, ...}]}]

    每层水平排列组件，层与层之间垂直排列。

    返回带 x, y, width, height 字段的节点列表，
    同时每个节点带有 layer_name 字段标记所属层。
    """
    result = []
    current_y = 0

    for layer in layers:
        layer_name = layer.get("name", "")
        components = layer.get("components", [])
        if not components:
            continue

        # 计算每个组件的宽度
        comp_widths = []
        for comp in components:
            if comp.get("width"):
                comp_widths.append(comp["width"])
            else:
                tw = estimate_text_width(comp.get("label", ""), font_size=20)
                comp_widths.append(max(tw + 60, 200))

        # 水平排列，计算起始 x（整体居中偏移，此处从 x=0 开始）
        current_x = 0
        layer_height = box_height

        for i, comp in enumerate(components):
            node_copy = dict(comp)
            node_copy["x"] = current_x
            node_copy["y"] = current_y
            node_copy["width"] = comp_widths[i]
            node_copy["height"] = box_height
            node_copy["layer_name"] = layer_name
            result.append(node_copy)
            current_x += comp_widths[i] + component_gap

        current_y += layer_height + layer_gap

    return result
