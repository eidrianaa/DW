"""MCP input validator.

Sanitises and validates tool arguments before they are dispatched to
handlers, enforcing pagination limits and required-field presence.
"""


def validate(tool_name: str, arguments: dict) -> dict:
    """Validate and sanitize tool input arguments.

    Parameters
    ----------
    tool_name:
        The name of the MCP tool being invoked.
    arguments:
        Raw arguments from the client.

    Returns
    -------
    dict
        A sanitised copy of *arguments*.

    Raises
    ------
    ValueError
        If a required field is missing or empty.
    """
    validated = dict(arguments)

    # Clamp pagination
    if "offset" in validated:
        validated["offset"] = max(0, int(validated["offset"]))
    if "limit" in validated:
        validated["limit"] = max(1, min(100, int(validated["limit"])))

    # Ensure required fields exist
    required_fields: dict[str, list[str]] = {
        "get_asset_details": ["assetId"],
        "get_data_source_details": ["dataSourceId"],
        "get_time_series_data": ["assetId", "dataSourceId", "startBusinessDate", "endBusinessDate"],
    }

    for field in required_fields.get(tool_name, []):
        if field not in validated or not validated[field]:
            raise ValueError(f"Missing required field: {field}")

    return validated
