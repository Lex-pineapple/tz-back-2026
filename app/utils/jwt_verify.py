from typing import Any, Dict
from jose import jwt

SECRET_KEY = "test-secret-key"
ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
