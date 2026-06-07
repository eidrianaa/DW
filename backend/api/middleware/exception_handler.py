"""FastAPI exception handlers.

Maps Python exceptions to structured JSON error responses so that
clients receive consistent error payloads.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exception with a generic 500 response.

    Parameters
    ----------
    request:
        The incoming request that triggered the exception.
    exc:
        The unhandled exception.

    Returns
    -------
    JSONResponse
        A JSON body with ``detail`` and ``error_code`` keys.
    """
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"},
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ``ValueError`` as a 400 Bad Request.

    Parameters
    ----------
    request:
        The incoming request.
    exc:
        The ``ValueError`` that was raised.

    Returns
    -------
    JSONResponse
        A JSON body echoing the error message.
    """
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_code": "VALIDATION_ERROR"},
    )
