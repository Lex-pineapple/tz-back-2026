from typing import TypedDict

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.database import init_db
from app.middlewares.exception_middleware import catch_exceptions_middleware
from app.middlewares.request_middleware import RequestMiddleware
from app.requests.router import router as requests_router
from app.auth.router import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

from app.utils.make_general_error import MakeGeneralErrorProps, make_general_error

app = FastAPI()

init_db()

app.add_middleware(RequestMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)
app.middleware("http")(catch_exceptions_middleware)
app.include_router(requests_router)
app.include_router(auth_router)


class ValidationErrorList(TypedDict):
    location: str
    message: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):

    errorData: list[ValidationErrorList] = []
    for error in exc.errors():
        errorData.append(
            {"location": " > ".join(error["loc"]), "message": error["msg"]}
        )
    errorMain = make_general_error(
        MakeGeneralErrorProps(
            status=400,
            error_type="validation_errors",
            error_message="Validation errors",
            error_metadata=errorData,
            message="There are some validation errors in your request",
            isError=True,
        )
    )
    return JSONResponse(content=errorMain, status_code=400)


@app.get("/")
def test_route():
    return {"message": "test message"}
