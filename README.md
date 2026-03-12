# excalidraw-mcp

Generate beautiful hand-drawn diagrams with AI. Flowcharts, architecture diagrams, and more — with **auto-layout**, **CJK support**, and **zero learning curve**.

> By [Maaker.AI](https://maaker.ai)

## Install

### Claude Desktop / Claude Code

Add to your MCP config:

```json
{
  "mcpServers": {
    "excalidraw": {
      "command": "uvx",
      "args": ["excalidraw-mcp"]
    }
  }
}
```

### pip

```bash
pip install excalidraw-mcp
```

## Tools

| Tool | Description |
|------|-------------|
| `create_flowchart` | Create flowcharts with auto-layout and smart arrow routing |
| `create_architecture_diagram` | Create layered architecture diagrams |
| `modify_diagram` | Add/remove nodes and connections in existing diagrams |
| `read_diagram` | Analyze existing `.excalidraw` files |
| `export_diagram` | Export to SVG |

## Quick Examples

### Flowchart

Just tell your AI assistant:

> "Create a flowchart: User Request → Load Balancer → API Server → Database"

The AI will call `create_flowchart` with structured data, and you'll get a `.excalidraw` file with:
- Auto-calculated box sizes based on text content
- Perfectly centered text (including Chinese/CJK characters)
- Smart arrow routing with proper edge binding
- Hand-drawn style that looks great in docs and presentations

### Architecture Diagram

> "Create an architecture diagram with Frontend (React, Next.js), Backend (API Server, Auth Service), and Database (PostgreSQL, Redis) layers"

Generates a layered diagram with components organized by tier, automatic sizing, and connections between layers.

### Read & Modify

> "Read the diagram at ./my-system.excalidraw and add a 'Cache' node connected to the API Server"

Works with existing `.excalidraw` files — read their structure, add/remove nodes, add connections.

## Why excalidraw-mcp?

### vs Official Excalidraw MCP (excalidraw/excalidraw-mcp)

| Feature | Official MCP | excalidraw-mcp |
|---------|-------------|----------------|
| **Approach** | Raw JSON — AI manually places every element | Structured input — say what you want, get a diagram |
| **Diagram types** | None (generic elements) | Flowcharts, architecture diagrams |
| **Layout** | AI calculates coordinates | Auto-layout (grid, layered) |
| **CJK text** | No width estimation | Accurate CJK/mixed-script width calculation |
| **Text centering** | AI must calculate x/y offsets | Automatic centering in containers |
| **Arrow binding** | AI must manage bindings | Automatic fixedPoint + orbit binding |
| **Local files** | Cannot read/write local files | Full read, modify, save support |
| **Distribution** | Remote URL / .mcpb | `uvx` / `pip` (standard Python) |
| **Token usage** | Needs `read_me` call to learn format | Format knowledge built-in |

### vs Mermaid-based tools

- **Free layout**: Not constrained by Mermaid syntax limitations
- **Hand-drawn style**: Native Excalidraw look, not rendered code blocks
- **Editable output**: Drag the `.excalidraw` file to excalidraw.com to continue editing

## Tool Reference

### `create_flowchart`

```
Input:
  nodes: [{label: "Step 1", color?: "blue"}]
  edges: [{from: "Step 1", to: "Step 2", label?: "next"}]
  direction?: "horizontal" | "vertical"
  title?: "My Flowchart"
  output_path?: "/path/to/output.excalidraw"

Output: Path to generated .excalidraw file
```

**Colors**: blue, green, purple, yellow, red, gray, orange, pink

### `create_architecture_diagram`

```
Input:
  layers: [{
    name: "Frontend",
    color?: "blue",
    components: [{label: "React"}, {label: "Next.js"}]
  }]
  connections?: [{from: "React", to: "API Server"}]
  output_path?: "/path/to/output.excalidraw"

Output: Path to generated .excalidraw file
```

### `modify_diagram`

```
Input:
  file_path: "/path/to/existing.excalidraw"
  add_nodes?: [{label: "New Node", color?: "green", x?: 100, y?: 100}]
  remove_labels?: ["Old Node"]
  add_connections?: [{from: "A", to: "B"}]
  output_path?: "/path/to/output.excalidraw"

Output: Path to modified file
```

### `read_diagram`

```
Input:
  file_path: "/path/to/diagram.excalidraw"

Output: Structured description (shapes, connections, colors)
```

### `export_diagram`

```
Input:
  file_path: "/path/to/diagram.excalidraw"
  format: "svg"

Output: Path to exported SVG file
```

## Technical Details

### CJK Width Estimation

Accurate text width calculation for mixed Chinese/English text:

| Character Type | Width (at fontSize=20) |
|---------------|----------------------|
| CJK characters | ~22px per character |
| ASCII letters/digits | ~11px per character |
| Spaces | ~5px |

### Arrow Binding

Uses Excalidraw's modern `fixedPoint` + `orbit` binding (not the deprecated `focus`/`gap` format):

```json
{
  "startBinding": {
    "elementId": "box1",
    "fixedPoint": [1.0, 0.5001],
    "mode": "orbit"
  }
}
```

Arrows automatically connect at the correct edge based on relative positions.

## Development

```bash
git clone https://github.com/maaker-ai/excalidraw-mcp.git
cd excalidraw-mcp
uv sync --dev
uv run pytest
```

## License

MIT
