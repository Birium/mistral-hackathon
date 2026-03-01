from mcp.server.fastmcp import FastMCP
from .tools import update, search, UPDATE_DESCRIPTION, SEARCH_DESCRIPTION

mcp = FastMCP("knower")

mcp.tool(
    description=UPDATE_DESCRIPTION,
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    meta={"type": "write"}
)(update)

mcp.tool(
    description=SEARCH_DESCRIPTION,
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    meta={"type": "read"}
)(search)