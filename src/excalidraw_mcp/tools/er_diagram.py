"""Entity-Relationship diagram tool."""

from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

from ..utils.ids import gen_id
from ..elements.text import create_labeled_shape, create_text, estimate_text_width
from ..elements.shapes import create_rectangle
from ..elements.arrows import create_arrow
from ..elements.style import get_color
from ..utils.file_io import save_excalidraw

# Layout constants
ENTITY_GAP = 300          # horizontal gap between entities
HEADER_HEIGHT = 40
ATTR_HEIGHT = 28
ATTR_FONT_SIZE = 14
HEADER_FONT_SIZE = 16
MIN_ENTITY_WIDTH = 180
ENTITY_PADDING = 30


def create_er_elements(
    entities: list[dict],
    relationships: list[dict],
    title: Optional[str] = None,
) -> list[dict]:
    """Create ER diagram elements.

    Args:
        entities: List of entity dicts with 'name' and 'attributes' (list of strings)
        relationships: List of dicts with 'from', 'to', 'label', optional cardinality
        title: Optional diagram title

    Returns:
        List of Excalidraw element dicts
    """
    elements = []
    entity_shapes = {}  # name -> header shape (for arrow binding)

    # 1. Layout entities horizontally
    current_x = 0
    for ent in entities:
        name = ent["name"]
        attrs = ent.get("attributes", [])
        color_name = ent.get("color", "blue")
        color = get_color(color_name)

        # Calculate width based on longest text
        all_texts = [name] + attrs
        max_text_width = max(estimate_text_width(t, HEADER_FONT_SIZE) for t in all_texts)
        entity_width = max(max_text_width + ENTITY_PADDING * 2, MIN_ENTITY_WIDTH)

        # Total entity height
        entity_height = HEADER_HEIGHT + len(attrs) * ATTR_HEIGHT

        # Header rectangle (colored)
        header_id = gen_id()
        header = create_rectangle(
            header_id,
            current_x, 0, entity_width, HEADER_HEIGHT,
            background_color=color["bg"],
            stroke_color=color["stroke"],
        )
        header["boundElements"] = []
        elements.append(header)

        # Header text
        header_text = create_text(
            gen_id(), name,
            x=current_x + (entity_width - estimate_text_width(name, HEADER_FONT_SIZE)) / 2,
            y=HEADER_HEIGHT / 2 - HEADER_FONT_SIZE * 0.7 / 2,
            font_size=HEADER_FONT_SIZE,
            container_id=header_id,
            width=estimate_text_width(name, HEADER_FONT_SIZE),
            height=HEADER_FONT_SIZE * 1.4,
        )
        header["boundElements"].append({"id": header_text["id"], "type": "text"})
        elements.append(header_text)

        # Body rectangle (white background)
        if attrs:
            body_id = gen_id()
            body_height = len(attrs) * ATTR_HEIGHT
            body = create_rectangle(
                body_id,
                current_x, HEADER_HEIGHT, entity_width, body_height,
                background_color="#ffffff",
                stroke_color=color["stroke"],
                strokeWidth=1,
            )
            elements.append(body)

            # Attribute texts
            for i, attr in enumerate(attrs):
                attr_text = create_text(
                    gen_id(), attr,
                    x=current_x + 10,
                    y=HEADER_HEIGHT + i * ATTR_HEIGHT + (ATTR_HEIGHT - ATTR_FONT_SIZE * 1.4) / 2,
                    font_size=ATTR_FONT_SIZE,
                    width=estimate_text_width(attr, ATTR_FONT_SIZE),
                    height=ATTR_FONT_SIZE * 1.4,
                )
                elements.append(attr_text)

        # Store for arrow connections — use a virtual shape spanning full entity
        entity_shapes[name] = {
            "id": header_id,
            "x": current_x,
            "y": 0,
            "width": entity_width,
            "height": entity_height,
            "boundElements": header.get("boundElements", []),
        }

        current_x += entity_width + ENTITY_GAP

    # 2. Draw relationships
    for rel in relationships:
        from_name = rel["from"]
        to_name = rel["to"]
        label = rel.get("label", "")
        from_card = rel.get("from_cardinality", "")
        to_card = rel.get("to_cardinality", "")

        from_shape = entity_shapes.get(from_name)
        to_shape = entity_shapes.get(to_name)
        if from_shape and to_shape:
            # Build full label with cardinality
            full_label = label
            if from_card or to_card:
                parts = []
                if from_card:
                    parts.append(from_card)
                parts.append(label or "—")
                if to_card:
                    parts.append(to_card)
                full_label = " ".join(parts)

            result = create_arrow(
                gen_id(), from_shape, to_shape,
                label=full_label if full_label else None,
            )
            elements.extend(result)

    # 3. Title
    if title:
        title_width = estimate_text_width(title, 24)
        title_text = create_text(
            gen_id(), title, x=0, y=-50,
            font_size=24, width=title_width,
        )
        elements.insert(0, title_text)

    return elements


class EREntity(BaseModel):
    name: str = Field(description="Entity name")
    attributes: list[str] = Field(default_factory=list, description="List of attribute names (use 'PK' suffix for primary keys)")
    color: Optional[str] = Field(default=None, description="Color name")


class ERRelationship(BaseModel):
    from_entity: str = Field(alias="from", description="Source entity name")
    to_entity: str = Field(alias="to", description="Target entity name")
    label: str = Field(default="", description="Relationship label (e.g., 'has many', 'belongs to')")
    from_cardinality: str = Field(default="", description="Source cardinality (e.g., '1', 'N', '0..1')")
    to_cardinality: str = Field(default="", description="Target cardinality (e.g., '1', 'N', '0..N')")

    model_config = {"populate_by_name": True}


def register_er_tools(mcp: FastMCP):
    @mcp.tool()
    def create_er_diagram(
        entities: list[EREntity],
        relationships: list[ERRelationship] | None = None,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """Create an Entity-Relationship (ER) diagram.

        Generates a database-style ER diagram with entity boxes showing
        attributes and relationship arrows with cardinality labels.

        Args:
            entities: List of entities with name and attributes
            relationships: List of relationships between entities
            title: Optional diagram title
            output_path: Optional output file path

        Returns:
            Absolute path to the generated .excalidraw file
        """
        ent_dicts = [
            {"name": e.name, "attributes": e.attributes, "color": e.color or "blue"}
            for e in entities
        ]

        rel_dicts = []
        if relationships:
            for r in relationships:
                rel_dicts.append({
                    "from": r.from_entity,
                    "to": r.to_entity,
                    "label": r.label,
                    "from_cardinality": r.from_cardinality,
                    "to_cardinality": r.to_cardinality,
                })

        elements = create_er_elements(ent_dicts, rel_dicts, title=title)

        path = output_path or "/tmp/er-diagram.excalidraw"
        result_path = save_excalidraw(elements, path)
        return f"ER diagram saved to: {result_path}\n\nOpen in Excalidraw: drag the file to https://excalidraw.com"
