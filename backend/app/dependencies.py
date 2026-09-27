"""Shared FastAPI dependencies (auth, DB session)."""

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import User
from app.services.user import UserService

logger = logging.getLogger(__name__)

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token")

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (ValueError, TypeError) as exc:
        raise credentials_exception from exc

    user = await UserService(session).get_by_id(user_id)
    if user is None:
        logger.warning("Token subject %s does not match any user", user_id)
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
