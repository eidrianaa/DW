#!/usr/bin/env python3
"""Seed script to populate the data warehouse with sample data."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from shared.database.cassandra_session import init_session, shutdown_session
from shared.database.schema_initializer import initialize_schema
from asset_context.domain.asset_aggregate import AssetAggregate
from asset_context.infrastructure.cassandra_asset_write_repo import CassandraAssetWriteRepo
from datasource_context.domain.data_source_aggregate import DataSourceAggregate
from datasource_context.infrastructure.cassandra_ds_write_repo import CassandraDataSourceWriteRepo
from datetime import datetime


def seed():
    print("Initializing Cassandra session...")
    init_session()
    initialize_schema()

    print("Seeding assets...")
    asset_repo = CassandraAssetWriteRepo()
    assets = [
        AssetAggregate(
            id="YFINANCE/AAPL", system_date=datetime.utcnow(),
            name="AAPL", description="Apple Inc.",
            attributes={"type": "equity", "exchange": "NASDAQ"},
        ),
        AssetAggregate(
            id="YFINANCE/GOOGL", system_date=datetime.utcnow(),
            name="GOOGL", description="Alphabet Inc.",
            attributes={"type": "equity", "exchange": "NASDAQ"},
        ),
        AssetAggregate(
            id="YFINANCE/MSFT", system_date=datetime.utcnow(),
            name="MSFT", description="Microsoft Corp.",
            attributes={"type": "equity", "exchange": "NASDAQ"},
        ),
        AssetAggregate(
            id="YFINANCE/BTC-USD", system_date=datetime.utcnow(),
            name="BTC-USD", description="Bitcoin / USD",
            attributes={"type": "crypto", "exchange": "CCC"},
        ),
        AssetAggregate(
            id="YFINANCE/TSLA", system_date=datetime.utcnow(),
            name="TSLA", description="Tesla Inc.",
            attributes={"type": "equity", "exchange": "NASDAQ"},
        ),
    ]
    for asset in assets:
        asset_repo.save(asset)
        print(f"  Created asset: {asset.id}")

    print("Seeding data sources...")
    ds_repo = CassandraDataSourceWriteRepo()
    sources = [
        DataSourceAggregate(
            id="YFINANCE", system_date=datetime.utcnow(),
            name="Yahoo Finance",
            description="Yahoo Finance via yfinance library",
            attributes={"Open", "Close", "High", "Low", "Volume"},
        ),
    ]
    for ds in sources:
        ds_repo.save(ds)
        print(f"  Created data source: {ds.id}")

    shutdown_session()
    print("Seeding complete!")


if __name__ == "__main__":
    seed()
