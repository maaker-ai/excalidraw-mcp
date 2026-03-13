import random
import time
from typing import Optional

from .shapes import create_rectangle, create_ellipse, create_diamond


def estimate_text_width(text: str, font_size: int = 20) -> float:
    """估算文字渲染宽度

    - CJK 字符 (U+4E00-U+9FFF, U+3400-U+4DBF, U+20000-U+2A6DF, U+F900-U+FAFF, U+2F800-U+2FA1F):
      font_size * 1.1
    - ASCII 字母/数字: font_size * 0.55
    - 空格: font_size * 0.25
    - 其他: font_size * 0.6
    """
    total = 0.0
    for ch in text:
        cp = ord(ch)
        if (0x4E00 <= cp <= 0x9FFF or
                0x3400 <= cp <= 0x4DBF or
                0x20000 <= cp <= 0x2A6DF or
                0xF900 <= cp <= 0xFAFF or
                0x2F800 <= cp <= 0x2FA1F or
                0x3000 <= cp <= 0x303F or  # CJK Symbols and Punctuation
                0xFF00 <= cp <= 0xFFEF):   # Halfwidth and Fullwidth Forms
            total += font_size * 1.1
        elif ch == ' ':
            total += font_size * 0.25
        elif ('a' <= ch <= 'z') or ('A' <= ch <= 'Z') or ('0' <= ch <= '9'):
            total += font_size * 0.55
        else:
            total += font_size * 0.6
    return total


FONT_FAMILIES = {
    "hand-drawn": 1, "hand_drawn": 1, "excalifont": 1,
    "normal": 2, "sans-serif": 2, "sans_serif": 2, "helvetica": 2,
    "code": 3, "monospace": 3, "mono": 3, "cascadia": 3,
}


def create_text(id: str, text: str, x: float, y: float,
                font_size: int = 20, container_id: Optional[str] = None,
                font_family: Optional[str] = None, **kwargs) -> dict:
    """创建文字元素。

    如果有 container_id，设置 containerId、textAlign="center"、verticalAlign="middle"、autoResize=true
    """
    width = kwargs.pop("width", estimate_text_width(text, font_size))
    height = kwargs.pop("height", font_size * 1.4)

    element = {
        "id": id,
        "type": "text",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "strokeColor": kwargs.pop("strokeColor", "#1e1e1e"),
        "backgroundColor": kwargs.pop("backgroundColor", "transparent"),
        "fillStyle": kwargs.pop("fillStyle", "solid"),
        "strokeWidth": kwargs.pop("strokeWidth", 2),
        "strokeStyle": kwargs.pop("strokeStyle", "solid"),
        "roughness": kwargs.pop("roughness", 1),
        "opacity": kwargs.pop("opacity", 100),
        "angle": kwargs.pop("angle", 0),
        "seed": kwargs.pop("seed", random.randint(1, 2**31)),
        "version": kwargs.pop("version", 1),
        "versionNonce": kwargs.pop("versionNonce", random.randint(1, 2**31)),
        "isDeleted": False,
        "groupIds": kwargs.pop("groupIds", []),
        "boundElements": kwargs.pop("boundElements", []),
        "updated": kwargs.pop("updated", int(time.time() * 1000)),
        "link": None,
        "locked": False,
        "roundness": None,
        "text": text,
        "fontSize": font_size,
        "fontFamily": kwargs.pop("fontFamily", FONT_FAMILIES.get(font_family or "", 1)),
        "textAlign": kwargs.pop("textAlign", "center" if container_id else "left"),
        "verticalAlign": kwargs.pop("verticalAlign", "middle" if container_id else "top"),
        "baseline": kwargs.pop("baseline", int(font_size * 0.8)),
    }

    if container_id:
        element["containerId"] = container_id
        element["autoResize"] = True
    else:
        element["containerId"] = None

    return element


from ..utils.ids import gen_id as _gen_id


def create_centered_title(title: str, elements: list[dict], y: float = -50, font_size: int = 24) -> dict:
    """Create a title text element centered over the bounding box of existing elements.

    Args:
        title: Title text
        elements: List of existing elements to center over
        y: Y position for the title
        font_size: Font size

    Returns:
        Title text element dict
    """
    # Compute bounding box of all elements that have x/width
    positioned = [e for e in elements if "x" in e and "width" in e]
    if positioned:
        min_x = min(e["x"] for e in positioned)
        max_x = max(e["x"] + e["width"] for e in positioned)
        content_center = (min_x + max_x) / 2
    else:
        content_center = 0

    tw = estimate_text_width(title, font_size)
    return create_text(
        _gen_id(), title,
        x=content_center - tw / 2, y=y,
        font_size=font_size, width=tw,
    )


def create_labeled_shape(
    shape_type: str,
    id: str,
    label: str,
    x: float,
    y: float,
    width: Optional[float] = None,
    height: float = 70,
    background_color: str = "#a5d8ff",
    font_size: int = 20,
    **kwargs
) -> tuple:
    """创建带标签的形状。

    自动：
    1. 估算文字宽度，如果 width 未指定则 width = max(text_width + 60, 200)
    2. 创建形状
    3. 创建文字，坐标居中
    4. 设置互相绑定（shape.boundElements 包含 text，text.containerId 指向 shape）

    返回 (shape_element, text_element)
    """
    if id is None:
        id = _gen_id()

    # Handle multi-line labels
    lines = label.split("\n")
    line_widths = [estimate_text_width(line, font_size) for line in lines]
    text_width = max(line_widths) if line_widths else estimate_text_width(label, font_size)
    if width is None:
        width = max(text_width + 60, 200)

    line_height = font_size * 1.4
    text_height = line_height * len(lines)

    # Auto-adjust container height for multi-line text
    if len(lines) > 1:
        min_height = text_height + 30  # padding
        height = max(height, min_height)

    # 生成文字 id
    text_id = id + "_text"

    # 形状的 boundElements 包含文字引用
    stroke_color = kwargs.pop("stroke_color", "#1e1e1e")
    shape_kwargs = dict(kwargs)
    shape_kwargs["boundElements"] = [{"id": text_id, "type": "text"}]

    # 创建形状
    if shape_type == "rectangle":
        shape = create_rectangle(id, x, y, width, height,
                                 background_color=background_color,
                                 stroke_color=stroke_color, **shape_kwargs)
    elif shape_type == "ellipse":
        shape = create_ellipse(id, x, y, width, height,
                               background_color=background_color,
                               stroke_color=stroke_color, **shape_kwargs)
    elif shape_type == "diamond":
        shape = create_diamond(id, x, y, width, height,
                               background_color=background_color,
                               stroke_color=stroke_color, **shape_kwargs)
    else:
        raise ValueError(f"不支持的形状类型: {shape_type}，请使用 rectangle/ellipse/diamond")

    # 文字坐标居中
    text_x = x + (width - text_width) / 2
    text_y = y + (height - text_height) / 2

    text_elem = create_text(
        text_id, label, text_x, text_y,
        font_size=font_size,
        container_id=id,
        width=text_width,
        height=text_height,
    )

    return (shape, text_elem)
