"""Unit tests for RunAggregationHandler and RunPredictionHandler (mocked SparkRunner)."""
import pytest
from unittest.mock import MagicMock
from analytics_context.commands.run_aggregation import (
    RunAggregationCommand,
    RunAggregationHandler,
)
from analytics_context.commands.run_prediction import (
    RunPredictionCommand,
    RunPredictionHandler,
)


@pytest.fixture
def mock_spark_runner():
    return MagicMock()


# ── RunAggregationHandler ────────────────────────────────────────────


class TestRunAggregationHandler:
    @pytest.mark.asyncio
    async def test_aggregation_handler_calls_spark(self, mock_spark_runner):
        mock_spark_runner.run_aggregation.return_value = 42
        handler = RunAggregationHandler(mock_spark_runner)
        result = await handler.handle(RunAggregationCommand())
        assert result["status"] == "completed"
        assert result["rows_aggregated"] == 42
        mock_spark_runner.run_aggregation.assert_called_once()

    @pytest.mark.asyncio
    async def test_aggregation_handler_passes_filter(self, mock_spark_runner):
        mock_spark_runner.run_aggregation.return_value = 10
        handler = RunAggregationHandler(mock_spark_runner)
        await handler.handle(RunAggregationCommand(data_source_filter="YFINANCE"))
        mock_spark_runner.run_aggregation.assert_called_once_with("YFINANCE")


# ── RunPredictionHandler ─────────────────────────────────────────────


class TestRunPredictionHandler:
    @pytest.mark.asyncio
    async def test_prediction_handler_calls_spark(self, mock_spark_runner):
        mock_spark_runner.run_prediction.return_value = {
            "count": 25,
            "model_name": "GBTRegressor",
            "metrics": {"rmse": 1.0, "r2": 0.95, "mae": 0.8},
            "all_models": [],
        }
        handler = RunPredictionHandler(mock_spark_runner)
        result = await handler.handle(
            RunPredictionCommand(asset_id="YFINANCE/AAPL", data_source_id="YFINANCE"),
        )
        assert result["status"] == "completed"
        assert result["predictions_generated"] == 25
        assert result["model_name"] == "GBTRegressor"
        assert result["metrics"]["r2"] == 0.95
        mock_spark_runner.run_prediction.assert_called_once_with(
            "YFINANCE/AAPL", "YFINANCE",
        )
