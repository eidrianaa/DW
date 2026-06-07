"""Run-anomaly-detection command and handler.

Launches a PySpark anomaly detection job that applies Z-score analysis
and Bollinger Band breach detection to OHLCV time-series data.
"""

from dataclasses import dataclass
from analytics_context.infrastructure.spark_runner import SparkRunner
from shared.mediator.types import Command, CommandHandler


@dataclass(frozen=True)
class RunAnomalyDetectionCommand(Command):
    """Command to run a Spark anomaly detection job.

    Attributes
    ----------
    asset_id : str
        The asset to analyse.
    data_source_id : str
        The data source that supplied the data.
    z_threshold : float
        Z-score threshold for anomaly flagging (default 2.5).
    """
    asset_id: str
    data_source_id: str
    z_threshold: float = 2.5


class RunAnomalyDetectionHandler(CommandHandler[RunAnomalyDetectionCommand]):
    """Handles ``RunAnomalyDetectionCommand`` by delegating to the Spark runner."""

    def __init__(self, spark_runner: SparkRunner):
        self._spark_runner = spark_runner

    async def handle(self, command: RunAnomalyDetectionCommand) -> dict:
        """Execute the anomaly detection job and return a summary."""
        result = self._spark_runner.run_anomaly_detection(
            command.asset_id, command.data_source_id,
            z_threshold=command.z_threshold,
        )
        return {
            "status": "completed",
            **result,
        }
