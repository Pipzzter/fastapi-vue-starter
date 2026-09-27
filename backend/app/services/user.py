import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        logger.debug("Fetched user by email %s => %s", email, bool(user))
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(
        self, payload: UserCreate, *, hashed_password: str | None = None
    ) -> UserRead:
        password_value = hashed_password or get_password_hash(payload.password)
        user = User(
            email=payload.email,
            hashed_password=password_value,
            full_name=payload.full_name,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info("Created user %s", user.email)
        return UserRead.model_validate(user)

    async def list_users(self) -> list[UserRead]:
        result = await self.session.execute(select(User))
        records = [UserRead.model_validate(user) for user in result.scalars().all()]
        logger.debug("List users returned %d records", len(records))
        return records
