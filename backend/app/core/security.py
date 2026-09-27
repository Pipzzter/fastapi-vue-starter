from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

settings = get_settings()
pwd_hasher = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hasher.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_hasher.hash(password)


def create_access_token(
    subject: str | int, expires_delta: timedelta | None = None
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid token") from exc
