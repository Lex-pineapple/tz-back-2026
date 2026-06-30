from typing import Awaitable, Callable

from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.context import user_id, permissions_var
from app.utils.make_general_error import MakeGeneralErrorProps, make_general_error
from app.utils.jwt_verify import verify_token
from starlette.types import ASGIApp


class RequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

        self.private_paths = {"/requests": ["DELETE"]}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        path = request.url.path
        method = request.method
        is_private_path = False
        for p in self.private_paths:
            is_private_path = p in path and method in self.private_paths[p]

        if is_private_path:
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return make_general_error(
                    MakeGeneralErrorProps(
                        status=401,
                        error_type="missing_auth_token",
                        error_message="Authorization header is missing or invalid",
                        error_metadata={},
                        message="Missing or invalid authorization token",
                    )
                )
            token = auth_header.split(" ")[1]

            try:
                decoded = verify_token(token)
                id = decoded.get("id")
                permissions = decoded.get("permissions", [])
                if not id:
                    return make_general_error(
                        MakeGeneralErrorProps(
                            status=401,
                            error_type="invalid_token_payload",
                            error_message="Token payload missing user_id",
                            error_metadata={},
                            message="Invalid token payload: missing user_id",
                        )
                    )
                permissions_var.set(permissions)
                user_id.set(id)
            except Exception as e:
                return make_general_error(
                    MakeGeneralErrorProps(
                        status=401,
                        error_type="invalid_token",
                        error_message=str(e),
                        error_metadata={},
                        message="Invalid or expired token",
                    )
                )

        response = await call_next(request)
        return response
