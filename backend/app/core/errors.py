"""Custom exception classes and FastAPI exception handlers."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class VeritasError(Exception):
    """Base application error mapped to a JSON response by the handler."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(VeritasError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(VeritasError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


class UnauthorizedError(VeritasError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"


class ValidationFailedError(VeritasError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_failed"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(VeritasError)
    async def _handle_veritas_error(_: Request, exc: VeritasError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("veritas_error", code=exc.code, message=exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
