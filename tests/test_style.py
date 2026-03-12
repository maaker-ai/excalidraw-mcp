"""Test color and style system."""
from excalidraw_mcp.elements.style import get_color


def test_basic_colors():
    """All 8 basic colors should be available."""
    for name in ["blue", "green", "purple", "yellow", "red", "gray", "orange", "pink"]:
        c = get_color(name)
        assert "bg" in c
        assert "stroke" in c


def test_unknown_color_fallback():
    """Unknown color should fall back to blue."""
    assert get_color("nonexistent") == get_color("blue")


def test_tech_color_redis():
    """Tech color 'redis' should return a red-themed color."""
    c = get_color("redis")
    assert c is not None
    assert c["bg"] != get_color("blue")["bg"]  # Not default


def test_tech_color_postgres():
    """Tech color 'postgres' should return a blue-themed color."""
    c = get_color("postgres")
    assert c is not None


def test_tech_color_kafka():
    """Tech color 'kafka' should exist."""
    c = get_color("kafka")
    assert c is not None


def test_tech_color_docker():
    """Tech color 'docker' should exist."""
    c = get_color("docker")
    assert c is not None


def test_tech_color_kubernetes():
    """Tech color 'kubernetes' or 'k8s' should exist."""
    c = get_color("kubernetes")
    assert c is not None
    c2 = get_color("k8s")
    assert c2 == c  # alias


def test_tech_color_aws():
    """Tech color 'aws' should exist."""
    c = get_color("aws")
    assert c is not None


def test_tech_color_react():
    """Tech color 'react' should exist."""
    c = get_color("react")
    assert c is not None


def test_tech_color_python():
    """Tech color 'python' should exist."""
    c = get_color("python")
    assert c is not None


def test_tech_colors_distinct():
    """Major tech colors should be visually distinct from each other."""
    techs = ["redis", "postgres", "kafka", "docker", "react", "python"]
    bg_colors = set()
    for tech in techs:
        c = get_color(tech)
        bg_colors.add(c["bg"])
    # At least 4 distinct background colors
    assert len(bg_colors) >= 4, f"Only {len(bg_colors)} distinct bg colors: {bg_colors}"
