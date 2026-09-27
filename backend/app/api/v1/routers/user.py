import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import CurrentUser
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserRead:
    service = UserService(session)
    logger.info("Creating user %s", payload.email)
    existing = await service.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    user = await service.create_user(payload)
    return user


@router.get("/", response_model=list[UserRead])
async def list_users(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[UserRead]:
    service = UserService(session)
    logger.debug("Listing users (requested by %s)", current_user.email)
    return await service.list_users()
