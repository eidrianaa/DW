"""Central router registry.

Collects every API router defined in the ``api.routers`` package and
provides a convenience function to mount them all on a FastAPI application.
"""

from fastapi import FastAPI

from api.routers import (
    analytics_router,
    asset_router,
    data_source_router,
    ingestion_router,
    time_series_router,
)

ALL_ROUTERS = [
    asset_router.router,
    data_source_router.router,
    time_series_router.router,
    ingestion_router.router,
    analytics_router.router,
]


def include_all_routers(app: FastAPI) -> None:
    """Include every registered API router on *app*.

    Parameters
    ----------
    app:
        The FastAPI application instance.
    """
    for r in ALL_ROUTERS:
        app.include_router(r)
