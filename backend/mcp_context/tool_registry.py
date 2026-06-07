"""MCP tool registry.

Centralises the JSON-Schema definitions for every tool exposed by the
MCP server so that LLM clients can discover available capabilities.
"""

from mcp.types import Tool


def get_tool_definitions() -> list[Tool]:
    """Return the complete list of MCP tool definitions.

    Each ``Tool`` includes a name, human-readable description, and a
    JSON-Schema ``inputSchema`` that LLM clients use for argument
    generation and validation.
    """
    return [
        Tool(
            name="list_assets",
            description="Returns a paginated list of financial asset IDs. Use for discovering available instruments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "offset": {"type": "integer", "default": 0},
                    "limit": {"type": "integer", "default": 20, "description": "1-100"},
                },
            },
        ),
        Tool(
            name="get_asset_details",
            description="Returns all temporal versions of a specific asset, latest first.",
            inputSchema={
                "type": "object",
                "properties": {"assetId": {"type": "string"}},
                "required": ["assetId"],
            },
        ),
        Tool(
            name="list_data_sources",
            description="Returns a paginated list of data source/provider IDs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "offset": {"type": "integer", "default": 0},
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="get_data_source_details",
            description="Returns details of a data source including supported attributes.",
            inputSchema={
                "type": "object",
                "properties": {"dataSourceId": {"type": "string"}},
                "required": ["dataSourceId"],
            },
        ),
        Tool(
            name="get_time_series_data",
            description="Returns time-series records for a given asset/source in a date range (max 365 days). Newest first, latest version only per business date.",
            inputSchema={
                "type": "object",
                "properties": {
                    "assetId": {"type": "string"},
                    "dataSourceId": {"type": "string"},
                    "startBusinessDate": {"type": "string", "description": "YYYY-MM-DD"},
                    "endBusinessDate": {"type": "string", "description": "YYYY-MM-DD"},
                    "includeAttributes": {"type": "boolean", "default": False},
                },
                "required": ["assetId", "dataSourceId", "startBusinessDate", "endBusinessDate"],
            },
        ),
    ]
