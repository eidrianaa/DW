"""PySpark ML prediction job with feature engineering and model selection.

Trains multiple regression models (Linear, GBT, Random Forest) on
engineered features derived from OHLCV time-series data. The best
model (by R-squared) is selected and its predictions are persisted.
"""

import logging
from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import (
    LinearRegression,
    GBTRegressor,
    RandomForestRegressor,
)
from pyspark.ml.evaluation import RegressionEvaluator

logger = logging.getLogger(__name__)


def _engineer_features(df: DataFrame) -> DataFrame:
    """Add derived features to the raw OHLCV dataframe.
    
    Features added:
    - prev_close: previous day's close (lag 1)
    - ma_3: 3-day simple moving average of close
    - ma_7: 7-day simple moving average of close
    - daily_return: (close - prev_close) / prev_close
    - spread: high - low (intraday range)
    - close_open_ratio: close / open
    - high_low_ratio: high / low
    """
    window_all = Window.orderBy("seconds")
    window_3 = Window.orderBy("seconds").rowsBetween(-2, 0)
    window_7 = Window.orderBy("seconds").rowsBetween(-6, 0)

    df = df.withColumn("prev_close", F.lag("close", 1).over(window_all))
    df = df.withColumn("ma_3", F.avg("close").over(window_3))
    df = df.withColumn("ma_7", F.avg("close").over(window_7))
    df = df.withColumn(
        "daily_return",
        F.when(F.col("prev_close") != 0, (F.col("close") - F.col("prev_close")) / F.col("prev_close")).otherwise(0.0),
    )
    df = df.withColumn("spread", F.col("high") - F.col("low"))
    df = df.withColumn(
        "close_open_ratio",
        F.when(F.col("open") != 0, F.col("close") / F.col("open")).otherwise(1.0),
    )
    df = df.withColumn(
        "high_low_ratio",
        F.when(F.col("low") != 0, F.col("high") / F.col("low")).otherwise(1.0),
    )

    # Drop rows where lag features are null (first row)
    return df.na.drop()


def _train_and_evaluate(
    train: DataFrame,
    test: DataFrame,
    features_col: str,
    label_col: str,
) -> list[dict]:
    """Train multiple models and return evaluation metrics for each.
    
    Returns a list of dicts: [{"name": ..., "model": ..., "rmse": ..., "r2": ..., "mae": ...}, ...]
    """
    evaluator_rmse = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="rmse")
    evaluator_r2 = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="r2")
    evaluator_mae = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="mae")

    candidates = [
        ("LinearRegression", LinearRegression(labelCol=label_col, featuresCol=features_col, maxIter=50, regParam=0.01, elasticNetParam=0.5)),
        ("GBTRegressor", GBTRegressor(labelCol=label_col, featuresCol=features_col, maxIter=50, maxDepth=5, stepSize=0.1)),
        ("RandomForest", RandomForestRegressor(labelCol=label_col, featuresCol=features_col, numTrees=100, maxDepth=8)),
    ]

    results = []
    for name, estimator in candidates:
        logger.info("Training model: %s", name)
        model = estimator.fit(train)
        preds = model.transform(test)
        rmse = evaluator_rmse.evaluate(preds)
        r2 = evaluator_r2.evaluate(preds)
        mae = evaluator_mae.evaluate(preds)
        logger.info("  %s -- RMSE=%.4f, R2=%.4f, MAE=%.4f", name, rmse, r2, mae)
        results.append({"name": name, "model": model, "rmse": rmse, "r2": r2, "mae": mae, "predictions": preds})
    
    return results


def run_prediction(cassandra_host: str, keyspace: str, asset_id: str, data_source_id: str) -> dict:
    """Run the full ML prediction pipeline.
    
    1. Loads OHLCV data from Cassandra
    2. Engineers features (lags, moving averages, ratios, volatility)
    3. Trains LinearRegression, GBTRegressor, RandomForestRegressor
    4. Evaluates each on test set (RMSE, R2, MAE)
    5. Selects best model by R2
    6. Writes predictions and feature data to Cassandra
    
    Returns dict with prediction count, winning model name, and metrics.
    """
    spark = SparkSession.builder \
        .appName("Adri DW - ML Prediction Pipeline") \
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
                   cast(unix_timestamp(business_date) as int) as seconds,
                   business_date as bdate
            FROM spark_data
            WHERE data_source_id = '{data_source_id}' AND asset_id = '{asset_id}'
              AND values_double['Open'] IS NOT NULL
        """).na.drop()

        row_count = df.count()
        if row_count < 30:
            logger.warning("Insufficient data for ML (%d rows). Need at least 30.", row_count)
            return {"count": 0, "model_name": "none", "metrics": {"rmse": 0, "r2": 0, "mae": 0}, "error": "insufficient_data"}

        # Write raw extracted data to regression_data
        df.write.format("org.apache.spark.sql.cassandra") \
            .options(table="regression_data", keyspace=keyspace).mode("append").save()

        # Feature engineering
        logger.info("Engineering features on %d rows", row_count)
        featured = _engineer_features(df)

        # Assemble feature vector
        feature_cols = ["seconds", "close", "low", "high", "prev_close", "ma_3", "ma_7", "daily_return", "spread", "close_open_ratio", "high_low_ratio"]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="raw_features")
        assembled = assembler.transform(featured)

        # Scale features
        scaler = StandardScaler(inputCol="raw_features", outputCol="features", withStd=True, withMean=True)
        scaler_model = scaler.fit(assembled)
        scaled = scaler_model.transform(assembled)

        # Train/test split
        train, test = scaled.randomSplit([0.7, 0.3], seed=42)
        logger.info("Train set: %d rows, Test set: %d rows", train.count(), test.count())

        # Multi-model training and evaluation
        results = _train_and_evaluate(train, test, features_col="features", label_col="open")

        # Select best model by R2
        best = max(results, key=lambda r: r["r2"])
        logger.info("Best model: %s (R2=%.4f)", best["name"], best["r2"])

        # Write predictions from best model
        preds = best["predictions"].select("seconds", "open", "prediction")
        preds.write.format("org.apache.spark.sql.cassandra") \
            .options(table="regression_results", keyspace=keyspace).mode("append").save()

        count = preds.count()
        return {
            "count": count,
            "model_name": best["name"],
            "metrics": {
                "rmse": round(best["rmse"], 6),
                "r2": round(best["r2"], 6),
                "mae": round(best["mae"], 6),
            },
            "all_models": [
                {"name": r["name"], "rmse": round(r["rmse"], 6), "r2": round(r["r2"], 6), "mae": round(r["mae"], 6)}
                for r in results
            ],
        }
    finally:
        spark.stop()
