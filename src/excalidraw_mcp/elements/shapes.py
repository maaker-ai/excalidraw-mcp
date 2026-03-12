import random
import string
import time


def _base_element(id: str, element_type: str, x: float, y: float, width: float, height: float,
                  background_color: str, stroke_color: str, **kwargs) -> dict:
    """构建基础形状元素的公共字段"""
    element = {
        "id": id,
        "type": element_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "strokeColor": stroke_color,
        "backgroundColor": background_color,
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
        "boundElements": kwargs.get("boundElements", []),
        "updated": kwargs.get("updated", int(time.time() * 1000)),
        "link": None,
        "locked": False,
        "roundness": kwargs.get("roundness", {"type": 3}),
    }
    return element


def create_rectangle(id: str, x: float, y: float, width: float, height: float,
                     background_color: str = "#a5d8ff", stroke_color: str = "#1e1e1e", **kwargs) -> dict:
    """创建矩形元素，返回完整的 Excalidraw JSON dict"""
    return _base_element(id, "rectangle", x, y, width, height, background_color, stroke_color, **kwargs)


def create_ellipse(id: str, x: float, y: float, width: float, height: float,
                   background_color: str = "#ffec99", stroke_color: str = "#1e1e1e", **kwargs) -> dict:
    """创建椭圆元素，返回完整的 Excalidraw JSON dict"""
    return _base_element(id, "ellipse", x, y, width, height, background_color, stroke_color, **kwargs)


def create_diamond(id: str, x: float, y: float, width: float, height: float,
                   background_color: str = "#ffc9c9", stroke_color: str = "#1e1e1e", **kwargs) -> dict:
    """创建菱形元素，返回完整的 Excalidraw JSON dict"""
    return _base_element(id, "diamond", x, y, width, height, background_color, stroke_color, **kwargs)
