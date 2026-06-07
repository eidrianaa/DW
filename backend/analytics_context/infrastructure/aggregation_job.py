from pyspark.sql import SparkSession

def run_aggregation(cassandra_host: str, keyspace: str, data_source_filter: str):
    print(f"\n[SPARK JOB] FILTRUL PRIMIT ESTE: '{data_source_filter}'\n")
    spark = SparkSession.builder \
        .appName("Adri DW - Aggregation") \
        .master("local[*]") \
        .config("spark.cassandra.connection.host", cassandra_host) \
        .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.13:3.5.0") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.driver.host", "127.0.0.1") \
        .getOrCreate()

    df = spark.read.format("org.apache.spark.sql.cassandra") \
        .options(table="data", keyspace=keyspace).load()
    df.createOrReplaceTempView("ts_data")

    totals = spark.sql("""
        SELECT asset_id, business_date_year, COUNT(*) as cnt
        FROM ts_data 
        WHERE data_source_id = 'NASDAQ-DATA-LINK'
        GROUP BY asset_id, business_date_year
    """)

    totals.write.format("org.apache.spark.sql.cassandra") \
        .options(table="totals", keyspace=keyspace).mode("append").save()

    count = totals.count()
    spark.stop()
    return count