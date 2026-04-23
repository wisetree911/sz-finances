import pytest
from app.core.security.security import (
    InvalidRefreshToken,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_of_refresh_token,
    hash_password,
    verify_password,
)


def test_hash_password_and_verify_password() -> None:
    password = 'super-secret-password'

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password('mewmew@3827', hashed) is False


def test_create_refresh_token_and_decode_refresh_token() -> None:
    token = create_refresh_token(user_id=42, jti='refresh-jti-1')

    user_id, jti = decode_refresh_token(token)

    assert user_id == 42
    assert jti == 'refresh-jti-1'


def test_decode_refresh_token_rejects_access_token() -> None:
    token = create_access_token(user_id=42)

    with pytest.raises(InvalidRefreshToken):
        decode_refresh_token(token)


def test_hash_of_refresh_token_is_deterministic() -> None:
    token = create_refresh_token(user_id=7, jti='same-token')

    first_hash = hash_of_refresh_token(token)
    second_hash = hash_of_refresh_token(token)

    assert first_hash == second_hash
