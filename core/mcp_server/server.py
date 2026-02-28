from mcp.server.fastmcp import FastMCP
from .tools import update, search

mcp = FastMCP("knower")

mcp.tool()(update)
mcp.tool()(search)