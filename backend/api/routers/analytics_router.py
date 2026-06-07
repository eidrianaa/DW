"""Analytics REST API router.

Provides endpoints for running Spark-based aggregation and ML prediction
jobs as well as retrieving their stored results.
"""

from fastapi import APIRouter, HTTPException, Query as Q
from pydantic import BaseModel, field_validator

from analytics_context.commands.run_aggregation import RunAggregationCommand
from analytics_context.commands.run_prediction import RunPredictionCommand
from analytics_context.commands.run_anomaly_detection import RunAnomalyDetectionCommand
from analytics_context.queries.get_aggregation_results import GetAggregationResultsQuery
from analytics_context.queries.get_prediction_results import GetPredictionResultsQuery
from analytics_context.queries.get_anomaly_results import GetAnomalyResultsQuery
from shared.mediator.command_bus import CommandBus
from shared.mediator.query_bus import QueryBus

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

_command_bus: CommandBus | None = None
_query_bus: QueryBus | None = None


def set_command_bus(bus: CommandBus) -> None:
    """Inject the command bus at startup."""
    global _command_bus
    _command_bus = bus


def set_query_bus(bus: QueryBus) -> None:
    """Inject the query bus at startup."""
    global _query_bus
    _query_bus = bus


class PredictionRequest(BaseModel):
    """Request body for the prediction endpoint."""

    asset_id: str
    data_source_id: str

    @field_validator("asset_id", "data_source_id")
    @classmethod
    def _must_not_be_empty(cls, v: str) -> str:
        """Ensure the field is not blank."""
        if not v or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class AnomalyDetectionRequest(BaseModel):
    """Request body for the anomaly detection endpoint."""

    asset_id: str
    data_source_id: str
    z_threshold: float = 2.5

    @field_validator("asset_id", "data_source_id")
    @classmethod
    def _must_not_be_empty(cls, v: str) -> str:
        """Ensure the field is not blank."""
        if not v or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


@router.post("/aggregate")
async def run_aggregation(data_source_filter: str = Q("YFINANCE")):
    """Launch a Spark aggregation job for the given data source."""
    result = await _command_bus.dispatch(
        RunAggregationCommand(data_source_filter=data_source_filter)
    )
    return result


@router.post("/predict")
async def run_prediction(request: PredictionRequest):
    """Launch a Spark ML prediction job for the given asset/source pair."""
    result = await _command_bus.dispatch(
        RunPredictionCommand(asset_id=request.asset_id, data_source_id=request.data_source_id)
    )
    return result


@router.get("/totals")
async def get_totals(asset_id: str | None = Q(None)):
    """Return stored aggregation totals, optionally filtered by asset."""
    result = await _query_bus.dispatch(GetAggregationResultsQuery(asset_id=asset_id))
    return result


@router.get("/predictions")
async def get_predictions():
    """Return stored ML prediction results."""
    result = await _query_bus.dispatch(GetPredictionResultsQuery())
    return result


@router.post("/anomalies")
async def run_anomaly_detection(request: AnomalyDetectionRequest):
    """Launch a Spark anomaly detection job for the given asset/source pair."""
    result = await _command_bus.dispatch(
        RunAnomalyDetectionCommand(
            asset_id=request.asset_id,
            data_source_id=request.data_source_id,
            z_threshold=request.z_threshold,
        )
    )
    return result


@router.get("/anomalies")
async def get_anomalies(asset_id: str | None = Q(None)):
    """Return detected anomalies, optionally filtered by asset."""
    result = await _query_bus.dispatch(GetAnomalyResultsQuery(asset_id=asset_id))
    return result
