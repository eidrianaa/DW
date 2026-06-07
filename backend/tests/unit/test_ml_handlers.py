"""Tests for the upgraded ML analytics command handlers."""
import pytest
from unittest.mock import MagicMock
from analytics_context.commands.run_prediction import RunPredictionCommand, RunPredictionHandler
from analytics_context.commands.run_anomaly_detection import RunAnomalyDetectionCommand, RunAnomalyDetectionHandler


class TestRunPredictionHandler:
    @pytest.mark.asyncio
    async def test_returns_model_metrics(self):
        mock_runner = MagicMock()
        mock_runner.run_prediction.return_value = {
            "count": 50,
            "model_name": "GBTRegressor",
            "metrics": {"rmse": 1.234, "r2": 0.95, "mae": 0.89},
            "all_models": [
                {"name": "LinearRegression", "rmse": 2.1, "r2": 0.80, "mae": 1.5},
                {"name": "GBTRegressor", "rmse": 1.234, "r2": 0.95, "mae": 0.89},
                {"name": "RandomForest", "rmse": 1.5, "r2": 0.90, "mae": 1.1},
            ],
        }
        handler = RunPredictionHandler(mock_runner)
        result = await handler.handle(RunPredictionCommand(asset_id="YFINANCE/AAPL", data_source_id="YFINANCE"))

        assert result["status"] == "completed"
        assert result["predictions_generated"] == 50
        assert result["model_name"] == "GBTRegressor"
        assert result["metrics"]["r2"] == 0.95
        assert len(result["all_models"]) == 3
        mock_runner.run_prediction.assert_called_once_with("YFINANCE/AAPL", "YFINANCE")

    @pytest.mark.asyncio
    async def test_handles_insufficient_data(self):
        mock_runner = MagicMock()
        mock_runner.run_prediction.return_value = {
            "count": 0,
            "model_name": "none",
            "metrics": {"rmse": 0, "r2": 0, "mae": 0},
            "error": "insufficient_data",
        }
        handler = RunPredictionHandler(mock_runner)
        result = await handler.handle(RunPredictionCommand(asset_id="X", data_source_id="Y"))
        assert result["predictions_generated"] == 0
        assert result["model_name"] == "none"


class TestRunAnomalyDetectionHandler:
    @pytest.mark.asyncio
    async def test_returns_anomaly_summary(self):
        mock_runner = MagicMock()
        mock_runner.run_anomaly_detection.return_value = {
            "total_anomalies": 12,
            "z_score_anomalies": 5,
            "bollinger_breaches": 8,
            "volume_spikes": 3,
        }
        handler = RunAnomalyDetectionHandler(mock_runner)
        result = await handler.handle(RunAnomalyDetectionCommand(
            asset_id="YFINANCE/AAPL", data_source_id="YFINANCE",
        ))

        assert result["status"] == "completed"
        assert result["total_anomalies"] == 12
        assert result["z_score_anomalies"] == 5
        assert result["bollinger_breaches"] == 8
        assert result["volume_spikes"] == 3
        mock_runner.run_anomaly_detection.assert_called_once_with(
            "YFINANCE/AAPL", "YFINANCE", z_threshold=2.5,
        )

    @pytest.mark.asyncio
    async def test_custom_z_threshold(self):
        mock_runner = MagicMock()
        mock_runner.run_anomaly_detection.return_value = {
            "total_anomalies": 0,
            "z_score_anomalies": 0,
            "bollinger_breaches": 0,
            "volume_spikes": 0,
        }
        handler = RunAnomalyDetectionHandler(mock_runner)
        await handler.handle(RunAnomalyDetectionCommand(
            asset_id="A", data_source_id="B", z_threshold=3.0,
        ))
        mock_runner.run_anomaly_detection.assert_called_once_with("A", "B", z_threshold=3.0)

    @pytest.mark.asyncio
    async def test_handles_insufficient_data(self):
        mock_runner = MagicMock()
        mock_runner.run_anomaly_detection.return_value = {
            "total_anomalies": 0,
            "z_score_anomalies": 0,
            "bollinger_breaches": 0,
            "volume_spikes": 0,
            "error": "insufficient_data",
        }
        handler = RunAnomalyDetectionHandler(mock_runner)
        result = await handler.handle(RunAnomalyDetectionCommand(
            asset_id="X", data_source_id="Y",
        ))
        assert result["total_anomalies"] == 0
