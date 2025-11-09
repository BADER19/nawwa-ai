import os
import time
from jose import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = "HS256"


def create_access_token(sub: str, minutes: int = 60) -> str:
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + minutes * 60}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
