import time
from typing import Awaitable, Callable

from fastapi import Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.context import user_id, permissions_var
from app.utils.jwt_verify import verify_token
from starlette.types import ASGIApp

class RequestMiddleware(BaseHTTPMiddleware):
  def __init__(self, app: ASGIApp):
    super().__init__(app)

    self.private_paths = {
        "/requests": ["DELETE"]
    }
  
  async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    path = request.url.path
    method = request.method
    is_private_path = False
    for p in self.private_paths:
      is_private_path = p in path and method in self.private_paths[p]

    if is_private_path:
      auth_header = request.headers.get("Authorization")

      if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            {
                "success": False,
                "status": 401,
                "data": None,
                "error": {
                    "type": "missing_auth_token",
                    "code": None,
                    "message": "Authorization header is missing or invalid",
                    "metadata": {}
                },
                "message": "Missing or invalid authorization token",
                "timestamp": int(time.time()),
            },
            status_code=401,
        )
      token = auth_header.split(" ")[1]

      try:
        decoded = verify_token(token)
        id = decoded.get("id")
        permissions = decoded.get("permissions", [])
        if not id:
          return JSONResponse(
              {
                  "success": False,
                  "status": 401,
                  "data": None,
                  "error": {
                      "type": "invalid_token_payload",
                      "code": None,
                      "message": "Token payload missing user_id",
                      "metadata": {}
                  },
                  "message": "Invalid token payload: missing user_id",
                  "timestamp": int(time.time()),
              },
              status_code=401,
          )
        permissions_var.set(permissions)      
        user_id.set(id)      
      except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "status": 401,
                "data": None,
                "error": {
                    "type": "invalid_token",
                    "code": None,
                    "message": str(e),
                    "metadata": {}
                },
                "message": "Invalid or expired token",
                "timestamp": int(time.time()),
            },
            status_code=401,
        )

    response = await call_next(request)
    return response