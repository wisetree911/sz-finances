from __future__ import annotations

from httpx import AsyncClient


async def register_user(
    client: AsyncClient,
    *,
    name: str = 'Test User',
    email: str = 'user@example.com',
    password: str = 'super-secret-password',
    role: str = 'user',
) -> dict:
    response = await client.post(
        '/api/auth/register',
        json={
            'name': name,
            'email': email,
            'password': password,
            'role': role,
        },
    )
    assert response.status_code == 201
    return response.json()


async def login_user(
    client: AsyncClient,
    *,
    email: str = 'user@example.com',
    password: str = 'super-secret-password',
) -> dict:
    response = await client.post(
        '/api/auth/login',
        data={
            'username': email,
            'password': password,
        },
    )
    assert response.status_code == 200
    return response.json()


async def test_register_login_and_get_current_user(client: AsyncClient) -> None:
    registered_user = await register_user(client)
    tokens = await login_user(client)

    me_response = await client.get(
        '/api/users/me',
        headers={'Authorization': f'Bearer {tokens["access_token"]}'},
    )

    assert registered_user == {
        'id': 1,
        'name': 'Test User',
        'email': 'user@example.com',
        'role': 'user',
    }
    assert tokens['token_type'] == 'bearer'
    assert 'access_token' in tokens
    assert 'refresh_token' in tokens
    assert me_response.status_code == 200
    assert me_response.json() == registered_user


async def test_users_me_requires_access_token(client: AsyncClient) -> None:
    response = await client.get('/api/users/me')

    assert response.status_code == 401


async def test_refresh_rotates_refresh_token(client: AsyncClient) -> None:
    await register_user(client)
    tokens = await login_user(client)

    refresh_response = await client.post(
        '/api/auth/refresh',
        json={'refresh_token': tokens['refresh_token']},
    )
    reused_refresh_response = await client.post(
        '/api/auth/refresh',
        json={'refresh_token': tokens['refresh_token']},
    )

    assert refresh_response.status_code == 200
    refreshed_tokens = refresh_response.json()
    assert refreshed_tokens['token_type'] == 'bearer'
    assert refreshed_tokens['refresh_token'] != tokens['refresh_token']
    assert reused_refresh_response.status_code == 401


async def test_logout_revokes_refresh_token(client: AsyncClient) -> None:
    await register_user(client)
    tokens = await login_user(client)

    logout_response = await client.post(
        '/api/auth/logout',
        json={'refresh_token': tokens['refresh_token']},
    )
    refresh_response = await client.post(
        '/api/auth/refresh',
        json={'refresh_token': tokens['refresh_token']},
    )

    assert logout_response.status_code == 204
    assert refresh_response.status_code == 401
