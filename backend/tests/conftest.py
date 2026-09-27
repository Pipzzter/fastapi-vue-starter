from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_session
from app.main import app as fastapi_app
from app.models.user import User as UserModel

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture()
async def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(db_engine):
    async_session = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session
        await _truncate_all_tables(session)


async def _truncate_all_tables(session: AsyncSession) -> None:
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()


@pytest_asyncio.fixture()
async def api_client(db_session):
    async def override_get_session():
        yield db_session

    fastapi_app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    fastapi_app.dependency_overrides.pop(get_session, None)


@pytest.fixture()
def mock_user_repository():
    session = AsyncMock(spec=AsyncSession)
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture()
def user_factory():
    def _factory(
        *,
        user_id: int = 1,
        email: str = "demo@example.com",
        full_name: str | None = "Demo",
        hashed_password: str = "hashed",
    ):
        user = UserModel(
            email=email, hashed_password=hashed_password, full_name=full_name
        )
        user.id = user_id
        return user

    return _factory
