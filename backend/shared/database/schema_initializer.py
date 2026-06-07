"""Cassandra schema initialiser.

Creates all required tables in the configured keyspace using
``CREATE TABLE IF NOT EXISTS`` so the statements are idempotent.
"""

import logging

from shared.database.cassandra_session import get_session

logger = logging.getLogger(__name__)


def initialize_schema() -> None:
    """Create all Cassandra tables needed by the application.

    Tables created: ``asset``, ``data_source``, ``data``, ``totals``,
    ``regression_data``, ``regression_results``.  Each statement is
    idempotent and will not error if the table already exists.
    """
    session = get_session()

    logger.info("Creating table 'asset' (if not exists)")
    session.execute("""
        CREATE TABLE IF NOT EXISTS asset (
            id TEXT,
            system_date TIMESTAMP,
            name TEXT,
            description TEXT,
            attributes MAP<TEXT, TEXT>,
            PRIMARY KEY (id, system_date)
        ) WITH CLUSTERING ORDER BY (system_date DESC)
    """)

    logger.info("Creating table 'data_source' (if not exists)")
    session.execute("""
        CREATE TABLE IF NOT EXISTS data_source (
            id TEXT,
            system_date TIMESTAMP,
            name TEXT,
            description TEXT,
            attributes SET<TEXT>,
            PRIMARY KEY (id, system_date)
        ) WITH CLUSTERING ORDER BY (system_date DESC)
    """)

    logger.info("Creating table 'data' (if not exists)")
    session.execute("""
        CREATE TABLE IF NOT EXISTS data (
            asset_id TEXT,
            data_source_id TEXT,
            business_date_year INT,
            business_date DATE,
            system_date TIMESTAMP,
            values_double MAP<TEXT, DOUBLE>,
            values_int MAP<TEXT, INT>,
            values_text MAP<TEXT, TEXT>,
            deleted BOOLEAN,
            PRIMARY KEY ((asset_id, data_source_id, business_date_year), business_date, system_date)
        ) WITH CLUSTERING ORDER BY (business_date DESC, system_date DESC)
    """)

    logger.info("Creating table 'totals' (if not exists)")
    session.execute("""
        CREATE TABLE IF NOT EXISTS totals (
            asset_id TEXT,
            business_date_year INT,
            cnt INT,
            PRIMARY KEY (asset_id, business_date_year)
        ) WITH CLUSTERING ORDER BY (business_date_year DESC)
    """)

    logger.info("Creating table 'regression_data' (if not exists)")
    session.execute("""
        CREATE TABLE IF NOT EXISTS regression_data (
            bdate DATE PRIMARY KEY,
            seconds INT,
            open DOUBLE,
            close DOUBLE,
            low DOUBLE,
            high DOUBLE
        )
    """)

    logger.info("Creating table 'regression_results' (if not exists)")
    session.execute("""
        CREATE TABLE IF NOT EXISTS regression_results (
            seconds INT PRIMARY KEY,
            open DOUBLE,
            prediction DOUBLE
        )
    """)

    logger.info("Creating table 'anomalies' (if not exists)")
    session.execute("""
        CREATE TABLE IF NOT EXISTS anomalies (
            asset_id TEXT,
            bdate DATE,
            close DOUBLE,
            z_score DOUBLE,
            z_flag BOOLEAN,
            bb_flag BOOLEAN,
            vol_flag BOOLEAN,
            PRIMARY KEY (asset_id, bdate)
        ) WITH CLUSTERING ORDER BY (bdate DESC)
    """)

    logger.info("Schema initialisation complete")
