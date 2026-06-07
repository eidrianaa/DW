"""PySpark anomaly detection job using statistical methods.

Detects price anomalies in time-series data using Z-score analysis
and Bollinger Band breach detection. Writes flagged anomalies to
the ``anomalies`` table in Cassandra.
"""

import logging
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)


def run_anomaly_detection(
    cassandra_host: str,
    keyspace: str,
    asset_id: str,
    data_source_id: str,
    z_threshold: float = 2.5,
    bollinger_window: int = 20,
    bollinger_std_mult: float = 2.0,
) -> dict:
    """Detect price anomalies using Z-score and Bollinger Bands.

    Methodology
    -----------
    1. **Z-score**: Compute the rolling mean and std of closing prices
       over a 20-day window.  Any close whose absolute Z-score exceeds
       ``z_threshold`` is flagged.
    2. **Bollinger Band breach**: Prices that close above the upper band
       or below the lower band are flagged.
    3. **Volume spike**: Days where volume exceeds 3x the 20-day average
       volume are additionally flagged.

    Returns a dict with the number of anomalies detected and a breakdown.
    """
    spark = SparkSession.builder \
        .appName("Adri DW - Anomaly Detection") \
        .config("spark.cassandra.connection.host", cassandra_host) \
        .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.5.0") \
        .getOrCreate()

    try:
        raw = spark.read.format("org.apache.spark.sql.cassandra") \
            .options(table="data", keyspace=keyspace).load()
        raw.createOrReplaceTempView("spark_data")

        df = spark.sql(f"""
            SELECT values_double['Open'] as open, values_double['Close'] as close,
                   values_double['Low'] as low, values_double['High'] as high,
                   values_double['Volume'] as volume,
                   cast(unix_timestamp(business_date) as int) as seconds,
                   business_date as bdate
            FROM spark_data
            WHERE data_source_id = '{data_source_id}' AND asset_id = '{asset_id}'
              AND values_double['Close'] IS NOT NULL
        """).na.drop()

        row_count = df.count()
        if row_count < bollinger_window + 5:
            logger.warning("Insufficient data for anomaly detection (%d rows)", row_count)
            return {"total_anomalies": 0, "z_score_anomalies": 0, "bollinger_breaches": 0, "volume_spikes": 0, "error": "insufficient_data"}

        window = Window.orderBy("seconds").rowsBetween(-bollinger_window + 1, 0)

        # Rolling statistics
        df = df.withColumn("rolling_mean", F.avg("close").over(window))
        df = df.withColumn("rolling_std", F.stddev("close").over(window))
        df = df.withColumn("rolling_vol_mean", F.avg("volume").over(window))

        # Z-score
        df = df.withColumn(
            "z_score",
            F.when(
                F.col("rolling_std") > 0,
                (F.col("close") - F.col("rolling_mean")) / F.col("rolling_std"),
            ).otherwise(0.0),
        )
        df = df.withColumn("is_z_anomaly", F.abs(F.col("z_score")) > z_threshold)

        # Bollinger Bands
        df = df.withColumn("bb_upper", F.col("rolling_mean") + bollinger_std_mult * F.col("rolling_std"))
        df = df.withColumn("bb_lower", F.col("rolling_mean") - bollinger_std_mult * F.col("rolling_std"))
        df = df.withColumn(
            "is_bb_breach",
            (F.col("close") > F.col("bb_upper")) | (F.col("close") < F.col("bb_lower")),
        )

        # Volume spike
        df = df.withColumn(
            "is_vol_spike",
            F.when(
                F.col("rolling_vol_mean") > 0,
                F.col("volume") > 3.0 * F.col("rolling_vol_mean"),
            ).otherwise(False),
        )

        # Combined anomaly flag
        df = df.withColumn(
            "is_anomaly",
            F.col("is_z_anomaly") | F.col("is_bb_breach") | F.col("is_vol_spike"),
        )

        # Drop nulls from rolling window warm-up
        df = df.na.drop()

        # Collect anomalies
        anomalies = df.filter(F.col("is_anomaly") == True).select(
            F.col("bdate").alias("business_date"),
            "open", "close", "high", "low", "volume",
            "z_score", "bb_upper", "bb_lower",
            "is_z_anomaly", "is_bb_breach", "is_vol_spike",
        )

        # Write to anomalies table
        anomaly_out = anomalies.select(
            F.col("business_date").alias("bdate"),
            F.lit(asset_id).alias("asset_id"),
            "close", "z_score",
            F.col("is_z_anomaly").cast("boolean").alias("z_flag"),
            F.col("is_bb_breach").cast("boolean").alias("bb_flag"),
            F.col("is_vol_spike").cast("boolean").alias("vol_flag"),
        )

        anomaly_out.write.format("org.apache.spark.sql.cassandra") \
            .options(table="anomalies", keyspace=keyspace).mode("append").save()

        # Compute summary
        total = anomalies.count()
        z_count = anomalies.filter(F.col("is_z_anomaly") == True).count()
        bb_count = anomalies.filter(F.col("is_bb_breach") == True).count()
        vol_count = anomalies.filter(F.col("is_vol_spike") == True).count()

        logger.info(
            "Anomaly detection complete: %d total (%d z-score, %d bollinger, %d volume)",
            total, z_count, bb_count, vol_count,
        )

        return {
            "total_anomalies": total,
            "z_score_anomalies": z_count,
            "bollinger_breaches": bb_count,
            "volume_spikes": vol_count,
        }
    finally:
        spark.stop()
