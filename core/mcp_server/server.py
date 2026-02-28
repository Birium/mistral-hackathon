from mcp.server.fastmcp import FastMCP
from .tools import (
    write,
    search
)

mcp = FastMCP("knower")

# Register all tools
mcp.tool()(search)
mcp.tool()(write)
