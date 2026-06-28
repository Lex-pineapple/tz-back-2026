from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.database import init_db
from app.middlewares.request_middleware import RequestMiddleware
from app.requests.router import router as requests_router
from app.auth.router import router as auth_router

from app.schemas import ValidationError

app = FastAPI()

init_db()

app.add_middleware(RequestMiddleware)
app.include_router(requests_router)
app.include_router(auth_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    errorData: ValidationError = {"type": "Validation errors","errors": []}
    for error in exc.errors():
        errorData['errors'].append({
            "location": " > ".join(error['loc']),
            "message": error['msg']
        })
    return JSONResponse(content=errorData, status_code=400)

@app.get('/')
def test_route():
    return {"message": "test message"}