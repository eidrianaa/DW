"""MCP server entry point for the Adri Financial Data Warehouse.

Exposes financial data warehouse tools (assets, data sources, time series)
to LLM clients via the Model Context Protocol over stdio transport.
"""

import json
import logging

from mcp.server import Server
from mcp.types import TextContent, Tool

from mcp_context.tool_registry import get_tool_definitions
from shared.database.cassandra_session import init_session
from shared.mediator.query_bus import QueryBus

logger = logging.getLogger(__name__)

app = Server("adri-financial-dw")
_query_bus: QueryBus | None = None


def initialize_mcp(query_bus: QueryBus) -> None:
    """Inject the query bus for tool dispatch.

    Parameters
    ----------
    query_bus:
        The application's ``QueryBus`` instance.
    """
    global _query_bus
    _query_bus = query_bus


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of available MCP tools."""
    return get_tool_definitions()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch a tool invocation to the appropriate handler.

    Parameters
    ----------
    name:
        The tool name as registered in the tool registry.
    arguments:
        Validated input arguments from the client.

    Returns
    -------
    list[TextContent]
        A single-element list containing the JSON-serialised result.
    """
    from mcp_context.tools.asset_tools import handle_asset_tool
    from mcp_context.tools.data_source_tools import handle_ds_tool
    from mcp_context.tools.time_series_tools import handle_ts_tool
    from mcp_context.validation.input_validator import validate

    try:
        validated = validate(name, arguments)

        if name in ("list_assets", "get_asset_details"):
            result = await handle_asset_tool(name, validated, _query_bus)
        elif name in ("list_data_sources", "get_data_source_details"):
            result = await handle_ds_tool(name, validated, _query_bus)
        elif name == "get_time_series_data":
            result = await handle_ts_tool(validated, _query_bus)
        else:
            result = {"error": "unknown_tool", "detail": f"Tool '{name}' not recognized"}
    except Exception:
        logger.exception("Error executing MCP tool %s", name)
        result = {"error": "internal_error", "detail": f"Failed to execute tool '{name}'"}

    return [TextContent(type="text", text=json.dumps(result, default=str))]
