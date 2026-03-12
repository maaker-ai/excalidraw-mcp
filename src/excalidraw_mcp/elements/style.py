# 颜色预设
COLORS: dict[str, dict[str, str]] = {
    "blue":   {"bg": "#a5d8ff", "stroke": "#1971c2"},
    "green":  {"bg": "#b2f2bb", "stroke": "#2f9e44"},
    "purple": {"bg": "#d0bfff", "stroke": "#7048e8"},
    "yellow": {"bg": "#ffec99", "stroke": "#e8590c"},
    "red":    {"bg": "#ffc9c9", "stroke": "#e03131"},
    "gray":   {"bg": "#dee2e6", "stroke": "#495057"},
    "orange": {"bg": "#ffd8a8", "stroke": "#e8590c"},
    "pink":   {"bg": "#fcc2d7", "stroke": "#c2255c"},
}


def get_color(name: str) -> dict[str, str]:
    """返回 {"bg": ..., "stroke": ...}，不存在时返回 blue"""
    return COLORS.get(name, COLORS["blue"])
