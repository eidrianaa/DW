"""Adri Financial Data Warehouse -- FastAPI application entry point.

Wires together the CQRS buses, domain event bus, Cassandra persistence,
all command/query handlers, and the REST API routers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.exception_handler import domain_exception_handler, value_error_handler
from api.router_registry import include_all_routers
from api.routers import (
    analytics_router,
    asset_router,
    data_source_router,
    ingestion_router,
    time_series_router,
)
from shared.config.settings import get_settings
from shared.database.cassandra_session import init_session, shutdown_session
from shared.database.schema_initializer import initialize_schema
from shared.events.event_bus import EventBus
from shared.mediator.command_bus import CommandBus
from shared.mediator.query_bus import QueryBus

# Import all commands & queries
from asset_context.commands.create_asset import CreateAssetCommand, CreateAssetHandler
from asset_context.commands.update_asset import UpdateAssetCommand, UpdateAssetHandler
from asset_context.commands.delete_asset import DeleteAssetCommand, DeleteAssetHandler
from asset_context.queries.list_assets import ListAssetsQuery, ListAssetsHandler
from asset_context.queries.get_asset_details import GetAssetDetailsQuery, GetAssetDetailsHandler
from datasource_context.commands.register_data_source import (
    RegisterDataSourceCommand,
    RegisterDataSourceHandler,
)
from datasource_context.queries.list_data_sources import ListDataSourcesQuery, ListDataSourcesHandler
from datasource_context.queries.get_data_source_details import (
    GetDataSourceDetailsQuery,
    GetDataSourceDetailsHandler,
)
from ingestion_context.commands.start_ingestion import StartIngestionCommand, StartIngestionHandler
from timeseries_context.queries.get_time_series import GetTimeSeriesQuery, GetTimeSeriesHandler
from analytics_context.commands.run_aggregation import RunAggregationCommand, RunAggregationHandler
from analytics_context.commands.run_prediction import RunPredictionCommand, RunPredictionHandler
from analytics_context.commands.run_anomaly_detection import (
    RunAnomalyDetectionCommand,
    RunAnomalyDetectionHandler,
)
from analytics_context.queries.get_aggregation_results import (
    GetAggregationResultsQuery,
    GetAggregationResultsHandler,
)
from analytics_context.queries.get_prediction_results import (
    GetPredictionResultsQuery,
    GetPredictionResultsHandler,
)
from analytics_context.queries.get_anomaly_results import (
    GetAnomalyResultsQuery,
    GetAnomalyResultsHandler,
)

logger = logging.getLogger(__name__)

command_bus = CommandBus()
query_bus = QueryBus()
event_bus = EventBus()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialise infrastructure on startup, tear down on shutdown."""
    logger.info("Starting Adri Financial Data Warehouse")
    try:
        init_session()
        initialize_schema()
    except Exception:
        logger.exception("Failed to initialise database -- aborting startup")
        raise
    _register_handlers()
    logger.info("Startup complete -- all handlers registered")
    yield
    logger.info("Shutting down Adri Financial Data Warehouse")
    shutdown_session()
    logger.info("Shutdown complete")


def _register_handlers() -> None:
    """Instantiate repositories and register every command/query handler."""
    from asset_context.infrastructure.cassandra_asset_write_repo import CassandraAssetWriteRepo
    from asset_context.infrastructure.cassandra_asset_read_repo import CassandraAssetReadRepo
    from datasource_context.infrastructure.cassandra_ds_write_repo import CassandraDataSourceWriteRepo
    from datasource_context.infrastructure.cassandra_ds_read_repo import CassandraDataSourceReadRepo
    from ingestion_context.infrastructure.yfinance_extractor import YFinanceExtractor
    from ingestion_context.infrastructure.record_transformer import RecordTransformer
    from ingestion_context.infrastructure.cassandra_ts_write_repo import CassandraTimeSeriesWriteRepo
    from timeseries_context.infrastructure.cassandra_ts_read_repo import CassandraTimeSeriesReadRepo
    from analytics_context.infrastructure.spark_runner import SparkRunner
    from analytics_context.infrastructure.cassandra_analytics_read_repo import CassandraAnalyticsReadRepo

    asset_write = CassandraAssetWriteRepo()
    asset_read = CassandraAssetReadRepo()
    ds_write = CassandraDataSourceWriteRepo()
    ds_read = CassandraDataSourceReadRepo()

    # Register command handlers
    command_bus.register(CreateAssetCommand, CreateAssetHandler(asset_write, event_bus))
    command_bus.register(UpdateAssetCommand, UpdateAssetHandler(asset_read, asset_write, event_bus))
    command_bus.register(DeleteAssetCommand, DeleteAssetHandler(asset_read, asset_write, event_bus))
    command_bus.register(RegisterDataSourceCommand, RegisterDataSourceHandler(ds_write))
    command_bus.register(StartIngestionCommand, StartIngestionHandler(
        YFinanceExtractor(), RecordTransformer(),
        CassandraTimeSeriesWriteRepo(),
        asset_write, asset_read, ds_write, ds_read, event_bus,
    ))
    command_bus.register(RunAggregationCommand, RunAggregationHandler(SparkRunner()))
    command_bus.register(RunPredictionCommand, RunPredictionHandler(SparkRunner()))
    command_bus.register(RunAnomalyDetectionCommand, RunAnomalyDetectionHandler(SparkRunner()))

    # Register query handlers
    query_bus.register(ListAssetsQuery, ListAssetsHandler(asset_read))
    query_bus.register(GetAssetDetailsQuery, GetAssetDetailsHandler(asset_read))
    query_bus.register(ListDataSourcesQuery, ListDataSourcesHandler(ds_read))
    query_bus.register(GetDataSourceDetailsQuery, GetDataSourceDetailsHandler(ds_read))
    query_bus.register(GetTimeSeriesQuery, GetTimeSeriesHandler(CassandraTimeSeriesReadRepo()))
    query_bus.register(GetAggregationResultsQuery, GetAggregationResultsHandler(CassandraAnalyticsReadRepo()))
    query_bus.register(GetPredictionResultsQuery, GetPredictionResultsHandler(CassandraAnalyticsReadRepo()))
    query_bus.register(GetAnomalyResultsQuery, GetAnomalyResultsHandler(CassandraAnalyticsReadRepo()))

    # Wire buses into routers
    asset_router.set_query_bus(query_bus)
    asset_router.set_command_bus(command_bus)
    data_source_router.set_query_bus(query_bus)
    data_source_router.set_command_bus(command_bus)
    time_series_router.set_query_bus(query_bus)
    ingestion_router.set_command_bus(command_bus)
    analytics_router.set_command_bus(command_bus)
    analytics_router.set_query_bus(query_bus)


settings = get_settings()

app = FastAPI(title="Adri Financial Data Warehouse", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, domain_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)

include_all_routers(app)


@app.get("/health")
async def health() -> dict:
    """Liveness probe endpoint."""
    return {"status": "ok"}
