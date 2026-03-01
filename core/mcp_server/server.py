from mcp.server.fastmcp import FastMCP
from .tools import update, search, UPDATE_DESCRIPTION, SEARCH_DESCRIPTION

mcp = FastMCP("knower")

mcp.tool(
    description=UPDATE_DESCRIPTION,
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    tags={"write", "vault"},
)(update)

mcp.tool(
    description=SEARCH_DESCRIPTION,
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    tags={"read", "vault"},
)(search)