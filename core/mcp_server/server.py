from mcp.server.fastmcp import FastMCP
from .tools import (
    tree,
    read,
    write,
    search,
    edit,
    append,
    delete,
    move
)

mcp = FastMCP("knower")

# Register all tools
mcp.tool()(tree)
mcp.tool()(read)
mcp.tool()(search)
mcp.tool()(write)
mcp.tool()(edit)
mcp.tool()(append)
mcp.tool()(delete)
mcp.tool()(move)
