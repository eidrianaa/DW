"""Spark job runner.

Thin wrapper around the PySpark aggregation and regression jobs,
providing a synchronous API that the command handlers can call.
"""

import logging

from shared.config.settings import get_settings

logger = logging.getLogger(__name__)


class SparkRunner:
    """Launches PySpark jobs using application settings for Cassandra connectivity."""

    def run_aggregation(self, data_source_filter: str) -> int:
        """Run the aggregation Spark job.

        Parameters
        ----------
        data_source_filter:
            Only rows with this ``data_source_id`` are aggregated.

        Returns
        -------
        int
            Number of aggregated rows written to the ``totals`` table.
        """
        settings = get_settings()
        logger.info("Starting Spark aggregation job (filter=%s)", data_source_filter)
        try:
            from analytics_context.infrastructure.aggregation_job import run_aggregation

            count = run_aggregation(
                settings.cassandra_hosts, settings.cassandra_keyspace, data_source_filter
            )
            logger.info("Aggregation job completed: %d rows", count)
            return count
        except Exception:
            logger.exception("Spark aggregation job failed")
            raise

    def run_prediction(self, asset_id: str, data_source_id: str) -> dict:
        """Run the ML prediction Spark job.

        Parameters
        ----------
        asset_id:
            The asset to train/predict on.
        data_source_id:
            The data source that supplied the training data.

        Returns
        -------
        dict
            Result dict with count, model_name, metrics, and all_models.
        """
        settings = get_settings()
        logger.info(
            "Starting Spark prediction job (asset=%s, source=%s)", asset_id, data_source_id
        )
        try:
            from analytics_context.infrastructure.regression_job import run_prediction

            result = run_prediction(
                settings.cassandra_hosts, settings.cassandra_keyspace, asset_id, data_source_id
            )
            logger.info("Prediction job completed: %d rows (model=%s)", result.get("count", 0), result.get("model_name", "unknown"))
            return result
        except Exception:
            logger.exception("Spark prediction job failed")
            raise

    def run_anomaly_detection(self, asset_id: str, data_source_id: str,
                               z_threshold: float = 2.5) -> dict:
        """Run anomaly detection Spark job."""
        settings = get_settings()
        logger.info("Starting anomaly detection (asset=%s, source=%s)", asset_id, data_source_id)
        try:
            from analytics_context.infrastructure.anomaly_job import run_anomaly_detection
            result = run_anomaly_detection(
                settings.cassandra_hosts, settings.cassandra_keyspace,
                asset_id, data_source_id, z_threshold=z_threshold,
            )
            logger.info("Anomaly detection completed: %d anomalies", result.get("total_anomalies", 0))
            return result
        except Exception:
            logger.exception("Anomaly detection job failed")
            raise
