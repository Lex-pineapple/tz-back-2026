from contextvars import ContextVar

user_id = ContextVar("user_id", default=None)
permissions_var = ContextVar("permissions", default=[])
