"""Tests for org chart tool."""

import os
from excalidraw_mcp.tools.org_chart import create_org_elements


def test_org_basic():
    """Basic org chart with hierarchy."""
    root = {
        "label": "CEO",
        "children": [
            {"label": "CTO", "children": [
                {"label": "Dev Lead"},
                {"label": "QA Lead"},
            ]},
            {"label": "CFO"},
        ]
    }
    elements = create_org_elements(root)
    assert len(elements) > 0

    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 4  # CEO, CTO, CFO, Dev Lead, QA Lead

    arrows = [e for e in elements if e["type"] == "arrow"]
    assert len(arrows) >= 3  # CEO->CTO, CEO->CFO, CTO->Dev, CTO->QA


def test_org_single():
    """Single node org chart."""
    root = {"label": "Solo"}
    elements = create_org_elements(root)
    rects = [e for e in elements if e["type"] == "rectangle"]
    assert len(rects) >= 1


def test_org_save(tmp_path):
    """Org chart saves to file."""
    from excalidraw_mcp.utils.file_io import save_excalidraw

    root = {
        "label": "Boss",
        "children": [{"label": "Employee"}]
    }
    elements = create_org_elements(root, title="Team Structure")
    path = str(tmp_path / "org.excalidraw")
    result = save_excalidraw(elements, path)
    assert os.path.exists(result)
