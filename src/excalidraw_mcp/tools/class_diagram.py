"""UML class diagram tool."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_text, estimate_text_width
from ..elements.shapes import create_rectangle
from ..elements.arrows import create_arrow
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
CLASS_GAP = 280          # horizontal gap between classes
HEADER_HEIGHT = 40
ATTR_HEIGHT = 24
METHOD_HEIGHT = 24
FONT_SIZE = 14
HEADER_FONT_SIZE = 16
MIN_CLASS_WIDTH = 180
PADDING = 20


def create_class_elements(
    classes: list[dict],
    relationships: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create UML class diagram elements.

    Args:
        classes: List of class dicts with 'name', 'attributes' (list[str]), 'methods' (list[str])
        relationships: List of relationship dicts with 'from', 'to', 'type' (inheritance/composition/aggregation/association)
        title: Optional diagram title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    class_shapes = {}  # name -> virtual shape for arrow binding

    current_x = 0
    for cls in classes:
        name = cls["name"]
        attrs = cls.get("attributes", [])
        methods = cls.get("methods", [])
        color_name = cls.get("color", "blue")
        color = get_color(color_name)

        # Calculate width from longest text
        all_texts = [name] + attrs + methods
        max_text_width = max(estimate_text_width(t, FONT_SIZE) for t in all_texts)
        class_width = max(max_text_width + PADDING * 2, MIN_CLASS_WIDTH)

        # Section heights
        attrs_height = max(len(attrs) * ATTR_HEIGHT, ATTR_HEIGHT)  # at least one row
        methods_height = max(len(methods) * METHOD_HEIGHT, METHOD_HEIGHT) if methods else 0
        total_height = HEADER_HEIGHT + attrs_height + methods_height

        # Header rectangle (class name)
        header_id = gen_id()
        header = create_rectangle(
            header_id,
            current_x, 0, class_width, HEADER_HEIGHT,
            background_color=color["bg"],
            stroke_color=color["stroke"],
        )
        header["boundElements"] = []
        elements.append(header)

        # Header text (class name, bold via font size)
        header_text = create_text(
            gen_id(), name,
            x=current_x + (class_width - estimate_text_width(name, HEADER_FONT_SIZE)) / 2,
            y=(HEADER_HEIGHT - HEADER_FONT_SIZE * 1.4) / 2,
            font_size=HEADER_FONT_SIZE,
            container_id=header_id,
            width=estimate_text_width(name, HEADER_FONT_SIZE),
            height=HEADER_FONT_SIZE * 1.4,
        )
        header["boundElements"].append({"id": header_text["id"], "type": "text"})
        elements.append(header_text)

        # Attributes section
        attrs_id = gen_id()
        attrs_rect = create_rectangle(
            attrs_id,
            current_x, HEADER_HEIGHT, class_width, attrs_height,
            background_color="#ffffff",
            stroke_color=color["stroke"],
            strokeWidth=1,
        )
        elements.append(attrs_rect)

        for i, attr in enumerate(attrs):
            attr_text = create_text(
                gen_id(), attr,
                x=current_x + 10,
                y=HEADER_HEIGHT + i * ATTR_HEIGHT + (ATTR_HEIGHT - FONT_SIZE * 1.4) / 2,
                font_size=FONT_SIZE,
                width=estimate_text_width(attr, FONT_SIZE),
                height=FONT_SIZE * 1.4,
            )
            elements.append(attr_text)

        # Methods section
        if methods:
            methods_id = gen_id()
            methods_y = HEADER_HEIGHT + attrs_height
            methods_rect = create_rectangle(
                methods_id,
                current_x, methods_y, class_width, methods_height,
                background_color="#ffffff",
                stroke_color=color["stroke"],
                strokeWidth=1,
            )
            elements.append(methods_rect)

            for i, method in enumerate(methods):
                method_text = create_text(
                    gen_id(), method,
                    x=current_x + 10,
                    y=methods_y + i * METHOD_HEIGHT + (METHOD_HEIGHT - FONT_SIZE * 1.4) / 2,
                    font_size=FONT_SIZE,
                    width=estimate_text_width(method, FONT_SIZE),
                    height=FONT_SIZE * 1.4,
                )
                elements.append(method_text)

        # Store shape for arrow connections
        class_shapes[name] = {
            "id": header_id,
            "x": current_x,
            "y": 0,
            "width": class_width,
            "height": total_height,
            "boundElements": header.get("boundElements", []),
        }

        current_x += class_width + CLASS_GAP

    # Relationships
    for rel in relationships:
        from_name = rel["from"]
        to_name = rel["to"]
        rel_type = rel.get("type", "association")
        label = rel.get("label", "")

        from_shape = class_shapes.get(from_name)
        to_shape = class_shapes.get(to_name)
        if from_shape and to_shape:
            # Determine arrowhead style based on relationship type
            kwargs = {}
            if rel_type == "inheritance":
                kwargs["endArrowhead"] = "triangle"
                kwargs["strokeStyle"] = "solid"
            elif rel_type == "composition":
                kwargs["endArrowhead"] = "diamond"
            elif rel_type == "aggregation":
                kwargs["endArrowhead"] = "diamond"
                kwargs["strokeStyle"] = "dashed"
            else:  # association
                kwargs["endArrowhead"] = "arrow"

            result = create_arrow(
                gen_id(), from_shape, to_shape,
                label=label if label else None,
                **kwargs,
            )
            elements.extend(result)

    # Title
    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title, x=0, y=-50,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    return elements


class ClassDef(BaseModel):
    name: str = Field(description="Class name")
    attributes: list[str] = Field(default_factory=list, description="List of attributes (e.g., 'name: string', '- id: int')")
    methods: list[str] = Field(default_factory=list, description="List of methods (e.g., 'getName()', '+ login(): bool')")
    color: Optional[str] = Field(default=None, description="Color name")


class ClassRelationship(BaseModel):
    from_class: str = Field(alias="from", description="Source class name")
    to_class: str = Field(alias="to", description="Target class name")
    type: str = Field(default="association", description="Relationship type: inheritance, composition, aggregation, association")
    label: str = Field(default="", description="Relationship label")

    model_config = {"populate_by_name": True}


def register_class_diagram_tools(mcp: FastMCP):
    @mcp.tool()
    def create_class_diagram(
        classes: list[ClassDef],
        relationships: list[ClassRelationship] | None = None,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        theme: str = "light",
    ) -> str:
        """Create a UML class diagram.

        Generates a class diagram with class boxes showing attributes and methods,
        connected by relationship arrows (inheritance, composition, etc.).

        Args:
            classes: List of class definitions with name, attributes, and methods
            relationships: List of relationships between classes
            title: Optional diagram title
            output_path: Optional output file path
            theme: Color theme - "light" or "dark"

        Returns:
            Absolute path to the generated .excalidraw file
        """
        cls_dicts = [
            {"name": c.name, "attributes": c.attributes, "methods": c.methods, "color": c.color or "blue"}
            for c in classes
        ]

        rel_dicts = []
        if relationships:
            for r in relationships:
                rel_dicts.append({
                    "from": r.from_class, "to": r.to_class,
                    "type": r.type, "label": r.label,
                })

        elements = create_class_elements(cls_dicts, rel_dicts, title=title)

        path = output_path or "/tmp/class-diagram.excalidraw"
        result_path = save_excalidraw(elements, path, theme=theme)
        return f"Class diagram saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
