import logging
from typing import Awaitable, Callable

from fastapi import Request, Response

from app.utils.make_general_error import MakeGeneralErrorProps, make_general_error


async def catch_exceptions_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    try:
        return await call_next(request)
    except Exception as e:
        logging.critical(e, exc_info=True)
        return make_general_error(
            MakeGeneralErrorProps(
                status=500,
                error_type="server_error",
                error_message="Server error occured",
                error_metadata={},
                message="Server error",
            )
        )
