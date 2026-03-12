import json
import os


def save_excalidraw(elements: list[dict], file_path: str) -> str:
    """保存为 .excalidraw 文件，返回绝对路径"""
    data = {
        "type": "excalidraw",
        "version": 2,
        "source": "maaker-ai/excalidraw-mcp",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
        "files": {}
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return os.path.abspath(file_path)


def load_excalidraw(file_path: str) -> dict:
    """加载 .excalidraw 文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
