from mcp.server.fastmcp import FastMCP

mcp = FastMCP("excalidraw-mcp")

# Register all tools
from excalidraw_mcp.tools.flowchart import register_flowchart_tools
from excalidraw_mcp.tools.architecture import register_architecture_tools
from excalidraw_mcp.tools.modify import register_modify_tools
from excalidraw_mcp.tools.export import register_export_tools
from excalidraw_mcp.tools.read import register_read_tools
from excalidraw_mcp.tools.sequence import register_sequence_tools
from excalidraw_mcp.tools.mermaid import register_mermaid_tools
from excalidraw_mcp.tools.mindmap import register_mindmap_tools
from excalidraw_mcp.tools.er_diagram import register_er_tools

register_flowchart_tools(mcp)
register_architecture_tools(mcp)
register_sequence_tools(mcp)
register_mermaid_tools(mcp)
register_mindmap_tools(mcp)
register_er_tools(mcp)
register_modify_tools(mcp)
register_export_tools(mcp)
register_read_tools(mcp)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
