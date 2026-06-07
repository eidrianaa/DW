"""Ingestion REST API router.

Provides the ``POST /api/v1/ingest`` endpoint that triggers data ingestion
from Yahoo Finance (or other configured providers) for a list of tickers.
"""

import re
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from ingestion_context.commands.start_ingestion import StartIngestionCommand
from shared.mediator.command_bus import CommandBus

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])

_command_bus: CommandBus | None = None

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_ALLOWED_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}


def set_command_bus(bus: CommandBus) -> None:
    """Inject the command bus at startup."""
    global _command_bus
    _command_bus = bus


class IngestionRequest(BaseModel):
    """Request body for the ingestion endpoint."""

    provider: str = "YFINANCE"
    dataset_codes: list[str]
    start_date: str | None = None
    end_date: str | None = None
    period: Literal[
        "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    ] | None = None

    @field_validator("start_date", "end_date")
    @classmethod
    def _validate_date_format(cls, v: str | None) -> str | None:
        """Ensure date strings match YYYY-MM-DD format."""
        if v is not None and not _DATE_RE.match(v):
            raise ValueError(f"Date must be in YYYY-MM-DD format, got '{v}'")
        return v


@router.post("")
async def trigger_ingestion(request: IngestionRequest):
    """Trigger data ingestion for the given tickers.

    The handler fetches OHLCV data, auto-creates missing asset and
    data-source records, and stores canonical time-series rows in
    Cassandra.
    """
    result = await _command_bus.dispatch(
        StartIngestionCommand(
            provider=request.provider,
            dataset_codes=request.dataset_codes,
            start_date=request.start_date,
            end_date=request.end_date,
            period=request.period,
        )
    )
    return result
