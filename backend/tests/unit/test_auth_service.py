from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from app.core.security.security import (
    create_refresh_token,
    hash_of_refresh_token,
    hash_password,
    verify_password,
)
from app.schemas.auth import RefreshToken
from app.schemas.user import UserRegister
from app.services.auth import AuthService
from fastapi import HTTPException


def make_service() -> AuthService:
    session = SimpleNamespace(add=Mock(), commit=AsyncMock())
    service = AuthService(session=session)
    service.user_repo = SimpleNamespace(
        get_by_email=AsyncMock(),
        create=AsyncMock(),
    )
    service.rs_repo = SimpleNamespace(
        create=AsyncMock(),
        get_by_jti=AsyncMock(),
        set_revoke_by_jti=AsyncMock(),
    )
    return service


def make_user(*, user_id: int = 1, password: str = 'correct-password') -> SimpleNamespace:
    return SimpleNamespace(
        id=user_id,
        name='Test User',
        email='user@example.com',
        role='user',
        hashed_password=hash_password(password),
    )


def make_refresh_session(
    *,
    token_hash: str,
    revoked_at=None,
    expires_at: datetime | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        user_id=42,
        jti='refresh-jti-1',
        token_hash=token_hash,
        revoked_at=revoked_at,
        expires_at=expires_at or (datetime.now(UTC) + timedelta(days=1)),
        replaced_by_jti=None,
    )


@pytest.mark.asyncio
async def test_login_rejects_incorrect_password() -> None:
    service = make_service()
    service.user_repo.get_by_email.return_value = make_user(password='correct-password')

    with pytest.raises(HTTPException) as exc:
        await service.login(username='user@example.com', password='wrong-password')

    assert exc.value.status_code == 400
    assert exc.value.detail == 'Incorrect username or password'
    service.rs_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_login_rejects_missing_user() -> None:
    service = make_service()
    service.user_repo.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.login(username='missing@example.com', password='any-password')

    assert exc.value.status_code == 400
    assert exc.value.detail == 'Incorrect username or password'
    service.rs_repo.create.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('refresh_session',),
    [
        (
            make_refresh_session(
                token_hash='will-be-overridden',
                revoked_at=datetime.now(UTC),
            ),
        ),
        (
            make_refresh_session(
                token_hash='will-be-overridden',
                expires_at=datetime.now(UTC) - timedelta(seconds=1),
            ),
        ),
        (
            make_refresh_session(
                token_hash='different-hash',
            ),
        ),
    ],
    ids=['revoked-session', 'expired-session', 'token-hash-mismatch'],
)
async def test_refresh_rejects_invalid_session_state(refresh_session: SimpleNamespace) -> None:
    service = make_service()
    refresh_token = create_refresh_token(user_id=42, jti='refresh-jti-1')
    payload = RefreshToken(refresh_token=refresh_token)

    if refresh_session.token_hash == 'will-be-overridden':
        refresh_session.token_hash = hash_of_refresh_token(refresh_token)

    service.rs_repo.get_by_jti.return_value = refresh_session

    with pytest.raises(HTTPException) as exc:
        await service.refresh(payload)

    assert exc.value.status_code == 401
    service.session.add.assert_not_called()
    service.session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_logout_ignores_invalid_refresh_token() -> None:
    service = make_service()

    await service.logout(RefreshToken(refresh_token='not-a-jwt'))

    service.rs_repo.set_revoke_by_jti.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email() -> None:
    service = make_service()
    service.user_repo.get_by_email.return_value = make_user()

    with pytest.raises(HTTPException) as exc:
        await service.register(
            UserRegister(
                name='New User',
                email='user@example.com',
                password='super-secret-password',
                role='user',
            )
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == 'User already exists'
    service.user_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_hashes_password_before_create() -> None:
    service = make_service()
    service.user_repo.get_by_email.return_value = None

    created_user = SimpleNamespace(
        id=7,
        name='New User',
        email='new@example.com',
        role='user',
    )
    service.user_repo.create.return_value = created_user

    response = await service.register(
        UserRegister(
            name='New User',
            email='new@example.com',
            password='super-secret-password',
            role='user',
        )
    )

    created_payload = service.user_repo.create.await_args.args[0]

    assert created_payload.hashed_password != 'super-secret-password'
    assert verify_password('super-secret-password', created_payload.hashed_password) is True
    assert response.id == 7
    assert response.name == 'New User'
    assert response.email == 'new@example.com'
    assert response.role == 'user'
