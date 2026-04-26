from __future__ import annotations

from typing import Any

from httpx import AsyncClient


async def register_user(
    client: AsyncClient,
    *,
    name: str,
    email: str,
    password: str = 'super-secret-password',
    role: str = 'user',
) -> dict[str, Any]:
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
    email: str,
    password: str = 'super-secret-password',
) -> dict[str, Any]:
    response = await client.post(
        '/api/auth/login',
        data={
            'username': email,
            'password': password,
        },
    )
    assert response.status_code == 200
    return response.json()


async def auth_headers(
    client: AsyncClient,
    *,
    name: str,
    email: str,
    role: str = 'user',
) -> tuple[dict[str, Any], dict[str, str]]:
    user = await register_user(client, name=name, email=email, role=role)
    tokens = await login_user(client, email=email)
    return user, {'Authorization': f'Bearer {tokens["access_token"]}'}


async def create_portfolio(
    client: AsyncClient,
    *,
    headers: dict[str, str],
    name: str,
    currency: str = 'RUB',
) -> dict[str, Any]:
    response = await client.post(
        '/api/portfolios/',
        headers=headers,
        json={
            'name': name,
            'currency': currency,
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_admin_portfolio(
    client: AsyncClient,
    *,
    headers: dict[str, str],
    user_id: int,
    name: str,
    currency: str = 'RUB',
) -> dict[str, Any]:
    response = await client.post(
        '/api/admin/portfolios/',
        headers=headers,
        json={
            'user_id': user_id,
            'name': name,
            'currency': currency,
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_portfolios_requires_access_token(client: AsyncClient) -> None:
    response = await client.get('/api/portfolios/')

    assert response.status_code == 401


async def test_portfolios_user_crud_flow(client: AsyncClient) -> None:
    user, headers = await auth_headers(
        client,
        name='Portfolio User',
        email='portfolio-user@example.com',
    )

    created = await create_portfolio(
        client,
        headers=headers,
        name='Main',
    )

    get_response = await client.get(
        f'/api/portfolios/{created["id"]}',
        headers=headers,
    )
    update_response = await client.patch(
        f'/api/portfolios/{created["id"]}',
        headers=headers,
        json={
            'name': 'Retirement',
            'currency': 'USD',
        },
    )
    list_response = await client.get('/api/portfolios/', headers=headers)
    delete_response = await client.delete(
        f'/api/portfolios/{created["id"]}',
        headers=headers,
    )
    deleted_get_response = await client.get(
        f'/api/portfolios/{created["id"]}',
        headers=headers,
    )

    assert created['user_id'] == user['id']
    assert created['name'] == 'Main'
    assert created['currency'] == 'RUB'
    assert 'created_at' in created

    assert get_response.status_code == 200
    assert get_response.json() == created

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['id'] == created['id']
    assert updated['user_id'] == user['id']
    assert updated['name'] == 'Retirement'
    assert updated['currency'] == 'USD'

    assert list_response.status_code == 200
    assert list_response.json() == [updated]

    assert delete_response.status_code == 204
    assert deleted_get_response.status_code == 404
    assert deleted_get_response.json() == {'detail': 'Portfolio not found'}


async def test_portfolios_list_returns_only_current_user_portfolios(
    client: AsyncClient,
) -> None:
    user, headers = await auth_headers(
        client,
        name='First User',
        email='first-user@example.com',
    )
    _, other_headers = await auth_headers(
        client,
        name='Second User',
        email='second-user@example.com',
    )

    own_portfolio = await create_portfolio(
        client,
        headers=headers,
        name='Visible',
    )
    await create_portfolio(
        client,
        headers=other_headers,
        name='Hidden',
    )

    response = await client.get('/api/portfolios/', headers=headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            **own_portfolio,
            'user_id': user['id'],
        }
    ]


async def test_portfolios_user_cannot_access_foreign_portfolio(client: AsyncClient) -> None:
    _, owner_headers = await auth_headers(
        client,
        name='Owner User',
        email='owner-user@example.com',
    )
    foreign_user, foreign_headers = await auth_headers(
        client,
        name='Foreign User',
        email='foreign-user@example.com',
    )
    portfolio = await create_portfolio(
        client,
        headers=owner_headers,
        name='Private',
    )

    get_response = await client.get(
        f'/api/portfolios/{portfolio["id"]}',
        headers=foreign_headers,
    )
    patch_response = await client.patch(
        f'/api/portfolios/{portfolio["id"]}',
        headers=foreign_headers,
        json={'name': 'Stolen'},
    )
    delete_response = await client.delete(
        f'/api/portfolios/{portfolio["id"]}',
        headers=foreign_headers,
    )

    assert foreign_user['id'] != portfolio['user_id']
    assert get_response.status_code == 404
    assert get_response.json() == {'detail': 'Portfolio not found'}
    assert patch_response.status_code == 404
    assert patch_response.json() == {'detail': 'Portfolio not found'}
    assert delete_response.status_code == 404
    assert delete_response.json() == {'detail': 'Portfolio not found'}


async def test_admin_portfolios_requires_admin_role(client: AsyncClient) -> None:
    _, headers = await auth_headers(
        client,
        name='Regular User',
        email='regular-user@example.com',
    )

    response = await client.get('/api/admin/portfolios/', headers=headers)

    assert response.status_code == 403
    assert response.json() == {'detail': 'Admin privileges required'}


async def test_admin_portfolios_crud_flow(client: AsyncClient) -> None:
    owner, _ = await auth_headers(
        client,
        name='Admin Portfolio Owner',
        email='admin-portfolio-owner@example.com',
    )
    _, admin_headers = await auth_headers(
        client,
        name='Admin User',
        email='admin-user@example.com',
        role='admin',
    )

    created = await create_admin_portfolio(
        client,
        headers=admin_headers,
        user_id=owner['id'],
        name='Managed',
    )

    get_response = await client.get(
        f'/api/admin/portfolios/{created["id"]}',
        headers=admin_headers,
    )
    update_response = await client.patch(
        f'/api/admin/portfolios/{created["id"]}',
        headers=admin_headers,
        json={
            'name': 'Managed Updated',
            'currency': 'USD',
        },
    )
    list_response = await client.get('/api/admin/portfolios/', headers=admin_headers)
    user_portfolios_response = await client.get(
        f'/api/admin/portfolios/user/{owner["id"]}',
        headers=admin_headers,
    )
    delete_response = await client.delete(
        f'/api/admin/portfolios/{created["id"]}',
        headers=admin_headers,
    )
    deleted_get_response = await client.get(
        f'/api/admin/portfolios/{created["id"]}',
        headers=admin_headers,
    )

    assert created['user_id'] == owner['id']
    assert created['name'] == 'Managed'
    assert created['currency'] == 'RUB'
    assert 'created_at' in created

    assert get_response.status_code == 200
    assert get_response.json() == created

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['id'] == created['id']
    assert updated['user_id'] == owner['id']
    assert updated['name'] == 'Managed Updated'
    assert updated['currency'] == 'USD'

    assert list_response.status_code == 200
    assert list_response.json() == {'portfolios': [updated]}

    assert user_portfolios_response.status_code == 200
    assert user_portfolios_response.json() == {'portfolios': [updated]}

    assert delete_response.status_code == 204
    assert deleted_get_response.status_code == 404
    assert deleted_get_response.json() == {'detail': 'SZ portfolio not found'}


async def test_admin_portfolios_returns_404_for_missing_portfolio(
    client: AsyncClient,
) -> None:
    _, admin_headers = await auth_headers(
        client,
        name='Missing Portfolio Admin',
        email='missing-portfolio-admin@example.com',
        role='admin',
    )

    response = await client.get('/api/admin/portfolios/999', headers=admin_headers)

    assert response.status_code == 404
    assert response.json() == {'detail': 'SZ portfolio not found'}
