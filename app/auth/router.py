from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
import bcrypt
from starlette import status
from app.core.database import get_db
from datetime import datetime, timedelta, timezone

from app.utils.make_general_error import MakeGeneralErrorProps, make_general_error
from .schemas import JWTPayload, JWTToken, Token

SECRET_KEY = "test-secret-key"
ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_brearer = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(
    prefix="/auth", tags=["auth"], responses={404: {"description": "Not Found"}}
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=make_general_error(
                MakeGeneralErrorProps(
                    status=401,
                    error_type="incorrect_credentials",
                    error_message="The password or username are incorrect",
                    error_metadata={},
                    message="Incorrect username or password",
                )
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        user["username"], user["id"], timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}


def auth_user(username: str, password: str):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return False
        if not bcrypt.checkpw(
            password.encode("utf-8"), user["hashed_password"].encode("utf-8")
        ):
            return False
        return dict(user)


def create_access_token(
    username: str, user_id: int, expires_delta: timedelta | None = None
) -> JWTToken:
    to_encode: JWTPayload = {"sub": username, "id": user_id, "permissions": ["*"]}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    excoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)
    return excoded_jwt
