FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .

# stdio MCP server — spoken to over stdin/stdout by the MCP client
ENTRYPOINT ["excalidraw-mcp"]
