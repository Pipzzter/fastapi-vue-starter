import logging
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_service = UserService(session)

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_service.get_by_email(email)
        logger.info("Authenticating user %s", email)
        if not user or not verify_password(password, user.hashed_password):
            logger.warning("Failed authentication for %s", email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return user

    async def register_user(self, payload: UserCreate) -> UserRead:
        user = await self.user_service.get_by_email(payload.email)
        logger.debug("Registering user %s", payload.email)
        if user:
            logger.warning("Registration attempt for existing email %s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed_password = get_password_hash(payload.password)
        return await self.user_service.create_user(
            payload, hashed_password=hashed_password
        )

    @staticmethod
    def generate_token(user_id: int, expires_delta: timedelta | None = None) -> Token:
        logger.debug("Generating token for user_id=%s", user_id)
        token = create_access_token(user_id, expires_delta)
        return Token(access_token=token, token_type="bearer")
