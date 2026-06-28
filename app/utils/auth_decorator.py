from typing import Awaitable, Callable, ParamSpec, TypeVar

from fastapi import HTTPException
from app.context import permissions_var
from functools import wraps

Param = ParamSpec("Param")
RetType = TypeVar("RetType")

class AuthDecorator:

  @staticmethod
  def require_access(permission: str):
    def decorator(func: Callable[Param, Awaitable[RetType]]) -> Callable[Param, Awaitable[RetType]]:
      @wraps(func)
      async def wrapper(*args: Param.args, **kwargs: Param.kwargs) ->  RetType:
        user_permissions = permissions_var.get() or []
        if "*" in user_permissions:
          return await func(*args, **kwargs)
        if permission not in user_permissions:
          raise HTTPException(
              status_code=403,
              detail={
                  "success": False,
                  "status": 403,
                  "message": f"Missing required permission: {permission}",
                  "error": {
                      "type": "missing_permission",
                      "metadata": {
                          "required_permission": permission,
                          "user_permissions": user_permissions,
                      },
                  },
              },
          )

        return await func(*args, **kwargs)
      return wrapper
    return decorator