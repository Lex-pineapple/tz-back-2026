from typing import Any, Mapping, TypedDict
import time

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class GeneralError(TypedDict):
    type: str
    code: int | None
    message: str
    metadata: Any


class GeneralErrorWrapper(TypedDict):
    success: bool
    status: int
    data: Any
    error: GeneralError
    message: str
    timestamp: int


class MakeGeneralErrorProps(BaseModel):
    status: int
    data: Any | None = None
    message: str
    error_type: str
    error_message: str
    error_metadata: Any
    isError: bool = False
    headers: Mapping[str, str] | None = None


def make_general_error(
    config: MakeGeneralErrorProps,
) -> JSONResponse | GeneralErrorWrapper:
    error_detail: GeneralErrorWrapper = {
        "success": False,
        "status": config.status,
        "data": config.data,
        "error": {
            "type": config.error_type,
            "code": config.status,
            "message": config.error_message,
            "metadata": config.error_metadata,
        },
        "message": config.message,
        "timestamp": int(time.time()),
    }

    if config.isError:
        return error_detail
    return JSONResponse(error_detail, status_code=config.status)
