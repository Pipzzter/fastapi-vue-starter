from typing import cast

import pytest
from pydantic import EmailStr, ValidationError

from app.schemas.user import UserCreate, UserLogin, UserRead


class _UserRecord:
    """Simple object to emulate ORM model for from_attributes tests."""

    def __init__(self, *, id_: int, email: EmailStr, full_name: str | None):
        self.id = id_
        self.email = email
        self.full_name = full_name


def test_user_create_valid_payload():
    payload = UserCreate(
        email=cast(EmailStr, "demo@example.com"),
        full_name="Demo",
        password="secret",
    )

    assert payload.email == "demo@example.com"
    assert payload.full_name == "Demo"
    assert payload.password == "secret"


def test_user_create_missing_email_raises():
    with pytest.raises(ValidationError):
        UserCreate(full_name="Demo", password="secret")


def test_user_create_missing_password_raises():
    with pytest.raises(ValidationError):
        UserCreate(email=cast(EmailStr, "demo@example.com"))


def test_user_create_full_name_optional_defaults_none():
    payload = UserCreate(email=cast(EmailStr, "demo@example.com"), password="secret")
    assert payload.full_name is None


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(email=cast(EmailStr, "demo@example.com"), password="")


def test_user_read_invalid_id_type_raises():
    with pytest.raises(ValidationError):
        UserRead(id="one", email=cast(EmailStr, "demo@example.com"), full_name=None)


def test_user_login_validates_email_format():
    login = UserLogin(email=cast(EmailStr, "demo@example.com"), password="secret")

    assert login.email == "demo@example.com"
    assert login.password == "secret"


def test_user_login_invalid_email_raises():
    with pytest.raises(ValidationError):
        UserLogin(email=cast(EmailStr, "not-an-email"), password="secret")


def test_user_read_excludes_password_from_model_validate():
    record = _UserRecord(
        id_=1, email=cast(EmailStr, "demo@example.com"), full_name=None
    )
    result = UserRead.model_validate(record)
    assert not hasattr(result, "hashed_password")
