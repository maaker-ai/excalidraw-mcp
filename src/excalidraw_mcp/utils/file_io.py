import json
import os


THEMES = {
    "light": {"viewBackgroundColor": "#ffffff"},
    "dark": {"viewBackgroundColor": "#1e1e1e"},
}


def save_excalidraw(elements: list[dict], file_path: str, theme: str = "light") -> str:
    """保存为 .excalidraw 文件，返回绝对路径。theme: 'light' 或 'dark'"""
    theme_config = THEMES.get(theme, THEMES["light"])
    data = {
        "type": "excalidraw",
        "version": 2,
        "source": "maaker-ai/excalidraw-mcp",
        "elements": elements,
        "appState": {"viewBackgroundColor": theme_config["viewBackgroundColor"], "gridSize": None},
        "files": {}
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return os.path.abspath(file_path)


def load_excalidraw(file_path: str) -> dict:
    """加载 .excalidraw 文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
