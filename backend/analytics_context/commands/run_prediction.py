"""Run-prediction command and handler.

Launches a PySpark ML regression job that trains a linear model on
historical OHLCV data and writes predictions to ``regression_results``.
"""

from dataclasses import dataclass

from analytics_context.infrastructure.spark_runner import SparkRunner
from shared.mediator.types import Command, CommandHandler


@dataclass(frozen=True)
class RunPredictionCommand(Command):
    """Command to run a Spark ML prediction job.

    Both fields are required -- they identify the exact asset/source
    combination to train on.

    Attributes
    ----------
    asset_id : str
        The asset to predict (e.g. ``YFINANCE/AAPL``).
    data_source_id : str
        The data source that supplied the training data.
    """

    asset_id: str
    data_source_id: str


class RunPredictionHandler(CommandHandler[RunPredictionCommand]):
    """Handles ``RunPredictionCommand`` by delegating to the Spark runner."""

    def __init__(self, spark_runner: SparkRunner):
        self._spark_runner = spark_runner

    async def handle(self, command: RunPredictionCommand) -> dict:
        """Execute the prediction job and return a summary with model metrics."""
        result = self._spark_runner.run_prediction(command.asset_id, command.data_source_id)
        return {
            "status": "completed",
            "predictions_generated": result.get("count", 0),
            "model_name": result.get("model_name", "unknown"),
            "metrics": result.get("metrics", {}),
            "all_models": result.get("all_models", []),
        }
