"""Unit tests for MCP input_validator."""
import pytest
from mcp_context.validation.input_validator import validate


class TestInputValidator:
    def test_clamps_offset_negative(self):
        result = validate("list_assets", {"offset": -5, "limit": 20})
        assert result["offset"] == 0

    def test_clamps_limit_over_100(self):
        result = validate("list_assets", {"offset": 0, "limit": 200})
        assert result["limit"] == 100

    def test_clamps_limit_under_1(self):
        result = validate("list_assets", {"offset": 0, "limit": 0})
        assert result["limit"] == 1

    def test_missing_required_field_raises(self):
        with pytest.raises(ValueError, match="Missing required field"):
            validate("get_asset_details", {})

    def test_valid_passthrough(self):
        result = validate(
            "get_asset_details",
            {"assetId": "TEST/ASSET", "offset": 0, "limit": 20},
        )
        assert result["assetId"] == "TEST/ASSET"
        assert result["offset"] == 0
        assert result["limit"] == 20

    def test_unknown_tool_no_required_fields(self):
        result = validate("some_unknown_tool", {"foo": "bar"})
        assert result["foo"] == "bar"
