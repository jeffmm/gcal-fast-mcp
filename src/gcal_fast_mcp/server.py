"""Google Calendar MCP Server — FastMCP v2 implementation."""

from fastmcp import FastMCP

mcp = FastMCP("Google Calendar")

# Importing tool modules triggers @mcp.tool() registration
from gcal_fast_mcp.tools import (  # noqa: E402, F401
    calendar_ops,
    event_ops,
    freebusy_ops,
)
