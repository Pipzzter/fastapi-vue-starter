from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from app.api.v1.routers import auth as auth_router
from app.api.v1.routers import health as health_router
from app.api.v1.routers import user as user_router
from app.dependencies import get_current_user
from app.main import app as fastapi_app


@pytest.fixture
def mock_user_service(monkeypatch):
    service = Mock()
    service.get_by_email = AsyncMock(return_value=None)
    service.create_user = AsyncMock(return_value=None)
    service.list_users = AsyncMock(return_value=[])
    monkeypatch.setattr(user_router, "UserService", lambda session: service)
    return service


@pytest.fixture
def mock_auth_service(monkeypatch):
    service = Mock()
    service.register_user = AsyncMock()
    service.authenticate_user = AsyncMock()
    service.generate_token = Mock()
    monkeypatch.setattr(auth_router, "AuthService", lambda session: service)
    return service


@pytest.fixture
def mock_health_service(monkeypatch):
    service = Mock()
    service.get_status = AsyncMock(
        return_value={
            "status": "ok",
            "timestamp": datetime.now(UTC),
        }
    )
    monkeypatch.setattr(health_router, "HealthService", lambda: service)
    return service


@pytest.fixture
def current_user():
    user = SimpleNamespace(id=1, email="me@example.com", full_name="Me")
    fastapi_app.dependency_overrides[get_current_user] = lambda: user
    yield user
    fastapi_app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture()
async def async_client(api_client):
    yield api_client
