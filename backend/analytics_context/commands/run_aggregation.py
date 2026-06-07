"""Run-aggregation command and handler.

Launches a PySpark aggregation job that groups time-series records by
asset and year, writing per-asset row counts into the ``totals`` table.
"""

from dataclasses import dataclass

from analytics_context.infrastructure.spark_runner import SparkRunner
from shared.mediator.types import Command, CommandHandler


@dataclass(frozen=True)
class RunAggregationCommand(Command):
    """Command to run a Spark aggregation job.

    Attributes
    ----------
    data_source_filter : str
        Only rows matching this data-source ID are aggregated.
    """

    data_source_filter: str = "YFINANCE"


class RunAggregationHandler(CommandHandler[RunAggregationCommand]):
    """Handles ``RunAggregationCommand`` by delegating to the Spark runner."""

    def __init__(self, spark_runner: SparkRunner):
        self._spark_runner = spark_runner

    async def handle(self, command: RunAggregationCommand) -> dict:
        """Execute the aggregation job and return a summary."""
        count = self._spark_runner.run_aggregation(command.data_source_filter)
        return {"status": "completed", "rows_aggregated": count}
