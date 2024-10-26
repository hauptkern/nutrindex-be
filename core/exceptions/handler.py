import re
from typing import Optional, Any
from uuid import uuid4
from fastapi.exceptions import RequestValidationError
from pydantic_core import PydanticSerializationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from core.logger import logging

logger = logging.getLogger(__name__)


def get_error_origin(obj: Any) -> str | None:
    try:
        if isinstance(obj, PydanticSerializationError):
            pattern = r"<class '([\w.]+)'>"
            match = re.search(pattern, str(obj))
            if match:
                class_name = match.group(1)
                return class_name
        if isinstance(obj, Exception):
            return type(obj).__name__
    except Exception:
        return None


def create_error_response(status_code: int, error_code: str, message: str,
                          exc: Optional[Exception] = None) -> JSONResponse:
    error_id = str(uuid4())
    log_error(error_id, status_code, error_code, message, exc)
    original_error_type = get_error_origin(exc)
    error_response = {
        "error": {
            "error_code": error_code,
            "message": message,
            "error_id": error_id,
            "error_type": original_error_type
        }
    }

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


def log_error(error_id: str, status_code: int, error_code: str, message: str, exc: Optional[Exception] = None):
    error_details = {
        "error_id": error_id,
        "status_code": status_code,
        "error_code": error_code,
        "message": message,
    }
    if exc:
        error_details["exception_type"] = get_error_origin(exc)
        error_details["exception_message"] = str(exc)

    logger.error(f"Error occurred: {error_details}", exc_info=exc)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="internal_server_error",
        message="An unexpected error occurred.",
        exc=exc
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="validation_error",
        message="The provided data is invalid. Please check your input and try again.",
        exc=exc
    )
