from fastmcp import FastMCP

from .tools import SEARCH_DESCRIPTION, UPDATE_DESCRIPTION, search, update

mcp = FastMCP("knower")

mcp.tool(
    description=UPDATE_DESCRIPTION,
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
    },
    tags=["write", "vault"],
)(update)

mcp.tool(
    description=SEARCH_DESCRIPTION,
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
    },
    tags=["search", "vault"],
)(search)
