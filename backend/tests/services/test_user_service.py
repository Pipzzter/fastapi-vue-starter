from unittest.mock import AsyncMock, Mock

import pytest

from app.schemas.user import UserCreate
from app.services.user import UserService

pytestmark = pytest.mark.asyncio


def _result_with_scalar(value):
    result = Mock()
    result.scalar_one_or_none.return_value = value
    return result


def _result_with_scalars(values):
    scalars_proxy = Mock()
    scalars_proxy.all.return_value = values
    result = Mock()
    result.scalars.return_value = scalars_proxy
    return result


async def test_get_by_email_returns_user(mock_user_repository, user_factory):
    service = UserService(mock_user_repository)
    expected_user = user_factory()
    mock_user_repository.execute.return_value = _result_with_scalar(expected_user)

    user = await service.get_by_email(expected_user.email)

    assert user is expected_user
    mock_user_repository.execute.assert_awaited_once()


async def test_get_by_email_handles_missing_user(mock_user_repository):
    service = UserService(mock_user_repository)
    mock_user_repository.execute.return_value = _result_with_scalar(None)

    user = await service.get_by_email("missing@example.com")

    assert user is None
    mock_user_repository.execute.assert_awaited_once()


async def test_create_user_hashes_password(monkeypatch, mock_user_repository):
    service = UserService(mock_user_repository)
    payload = UserCreate(email="hash@example.com", password="secret")
    fake_hash = "hashed-secret"
    monkeypatch.setattr("app.services.user.get_password_hash", lambda _: fake_hash)

    async def _refresh_side_effect(user):
        user.id = 1

    mock_user_repository.refresh = AsyncMock(side_effect=_refresh_side_effect)

    mock_user_repository.execute.return_value = _result_with_scalar(None)

    created = await service.create_user(payload)

    assert created.email == payload.email
    assert created.id == 1
    added_user = mock_user_repository.add.call_args.args[0]
    assert added_user.hashed_password == fake_hash
    mock_user_repository.commit.assert_awaited_once()
    mock_user_repository.refresh.assert_awaited_once()


async def test_create_user_respects_provided_hash(monkeypatch, mock_user_repository):
    service = UserService(mock_user_repository)
    payload = UserCreate(email="hash@example.com", password="secret")
    monkeypatch.setattr(
        "app.services.user.get_password_hash",
        lambda _: (_ for _ in ()).throw(RuntimeError("should not hash")),
    )

    async def _refresh_side_effect(user):
        user.id = 2

    mock_user_repository.refresh = AsyncMock(side_effect=_refresh_side_effect)

    mock_user_repository.execute.return_value = _result_with_scalar(None)

    created = await service.create_user(payload, hashed_password="pref-hash")

    assert created.id == 2
    added_user = mock_user_repository.add.call_args.args[0]
    assert added_user.hashed_password == "pref-hash"


async def test_list_users_returns_serialized_models(mock_user_repository, user_factory):
    service = UserService(mock_user_repository)
    first = user_factory(user_id=1, email="first@example.com")
    second = user_factory(user_id=2, email="second@example.com")
    mock_user_repository.execute.return_value = _result_with_scalars([first, second])

    users = await service.list_users()

    assert [u.email for u in users] == ["first@example.com", "second@example.com"]
    mock_user_repository.execute.assert_awaited_once()
