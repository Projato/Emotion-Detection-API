from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi.errors import RateLimitExceeded

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        f"Unhandled server error | method={request.method} path={request.url.path} error={str(exc)}"
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    logger.warning(
        f"Rate limit exceeded | method={request.method} path={request.url.path} client={request.client.host if request.client else 'unknown'}"
    )
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded"},
    )