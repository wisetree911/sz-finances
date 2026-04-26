from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.models.asset import Asset
from app.models.portfolio import Portfolio
from app.models.trade import Trade
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


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


async def create_asset(
    db_session: AsyncSession,
    *,
    ticker: str = 'SBER',
    full_name: str = 'Sberbank',
    sector: str = 'financials',
) -> Asset:
    asset = Asset(ticker=ticker, full_name=full_name, type='stock', sector=sector)
    db_session.add(asset)
    await db_session.flush()
    return asset


async def create_portfolio(
    db_session: AsyncSession,
    *,
    user_id: int,
    name: str = 'Main',
    currency: str = 'RUB',
) -> Portfolio:
    portfolio = Portfolio(user_id=user_id, name=name, currency=currency)
    db_session.add(portfolio)
    await db_session.flush()
    return portfolio


def make_trade(
    *,
    portfolio_id: int,
    asset_id: int,
    direction: str = 'buy',
    quantity: Decimal = Decimal('1'),
    price: Decimal = Decimal('100'),
    trade_time: datetime | None = None,
) -> Trade:
    return Trade(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        direction=direction,
        quantity=quantity,
        price=price,
        trade_time=trade_time or datetime.now(UTC),
    )


async def test_trade_requires_access_token(client: AsyncClient) -> None:
    response = await client.get('/api/trades/1')

    assert response.status_code == 401


async def test_get_trade_for_user_returns_owner_trade(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user, headers = await auth_headers(
        client,
        name='Trade Owner',
        email='trade-owner@example.com',
    )
    asset = await create_asset(db_session)
    portfolio = await create_portfolio(db_session, user_id=user['id'])
    trade = make_trade(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal('2'),
        price=Decimal('123.45'),
        trade_time=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
    )
    db_session.add(trade)
    await db_session.commit()
    await db_session.refresh(trade)

    response = await client.get(f'/api/trades/{trade.id}', headers=headers)

    assert response.status_code == 200
    payload = response.json()

    assert payload['id'] == trade.id
    assert payload['portfolio_id'] == portfolio.id
    assert payload['asset_id'] == asset.id
    assert payload['direction'] == 'buy'
    assert Decimal(str(payload['quantity'])) == Decimal('2')
    assert Decimal(str(payload['price'])) == Decimal('123.45')
    assert payload['trade_time'].startswith('2024-01-01T12:00:00')
    assert 'created_at' in payload


async def test_get_trade_for_user_returns_404_for_foreign_trade(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    owner, _ = await auth_headers(
        client,
        name='Trade Owner',
        email='foreign-trade-owner@example.com',
    )
    _, headers = await auth_headers(
        client,
        name='Foreign User',
        email='foreign-trade-user@example.com',
    )
    asset = await create_asset(db_session)
    portfolio = await create_portfolio(db_session, user_id=owner['id'])
    trade = make_trade(portfolio_id=portfolio.id, asset_id=asset.id)
    db_session.add(trade)
    await db_session.commit()
    await db_session.refresh(trade)

    response = await client.get(f'/api/trades/{trade.id}', headers=headers)

    assert response.status_code == 404
    assert response.json() == {'detail': 'SZ trade not found'}


async def test_get_portfolio_trades_for_user_returns_only_owner_trades(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    owner, headers = await auth_headers(
        client,
        name='Portfolio Trades Owner',
        email='portfolio-trades-owner@example.com',
    )
    other_user, _ = await auth_headers(
        client,
        name='Other Owner',
        email='other-trade-owner@example.com',
    )
    asset = await create_asset(db_session)
    owner_portfolio = await create_portfolio(db_session, user_id=owner['id'])
    other_portfolio = await create_portfolio(
        db_session,
        user_id=other_user['id'],
        name='Other',
    )
    first_trade = make_trade(
        portfolio_id=owner_portfolio.id,
        asset_id=asset.id,
        quantity=Decimal('1'),
        price=Decimal('100'),
    )
    second_trade = make_trade(
        portfolio_id=owner_portfolio.id,
        asset_id=asset.id,
        quantity=Decimal('3'),
        price=Decimal('110'),
    )
    foreign_trade = make_trade(
        portfolio_id=other_portfolio.id,
        asset_id=asset.id,
        quantity=Decimal('5'),
        price=Decimal('120'),
    )
    db_session.add_all([first_trade, second_trade, foreign_trade])
    await db_session.commit()
    await db_session.refresh(first_trade)
    await db_session.refresh(second_trade)
    await db_session.refresh(foreign_trade)

    response = await client.get(
        f'/api/trades/portfolio/{owner_portfolio.id}',
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.json()

    assert len(payload) == 2
    assert {item['id'] for item in payload} == {first_trade.id, second_trade.id}
    assert all(item['portfolio_id'] == owner_portfolio.id for item in payload)


async def test_get_portfolio_trades_for_user_returns_404_for_foreign_portfolio(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    owner, _ = await auth_headers(
        client,
        name='Protected Portfolio Owner',
        email='protected-portfolio-owner@example.com',
    )
    _, headers = await auth_headers(
        client,
        name='Protected Portfolio User',
        email='protected-portfolio-user@example.com',
    )
    asset = await create_asset(db_session)
    portfolio = await create_portfolio(db_session, user_id=owner['id'])
    db_session.add(make_trade(portfolio_id=portfolio.id, asset_id=asset.id))
    await db_session.commit()

    response = await client.get(
        f'/api/trades/portfolio/{portfolio.id}',
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'SZ trades not found'}


async def test_admin_trades_requires_admin_role(client: AsyncClient) -> None:
    _, headers = await auth_headers(
        client,
        name='Regular Trade User',
        email='regular-trade-user@example.com',
    )

    response = await client.get('/api/admin/trades/', headers=headers)

    assert response.status_code == 403
    assert response.json() == {'detail': 'Admin privileges required'}


async def test_admin_trades_crud_flow(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    owner, _ = await auth_headers(
        client,
        name='Trade Admin Owner',
        email='trade-admin-owner@example.com',
    )
    _, admin_headers = await auth_headers(
        client,
        name='Trade Admin',
        email='trade-admin@example.com',
        role='admin',
    )
    asset = await create_asset(db_session)
    portfolio = await create_portfolio(db_session, user_id=owner['id'])
    await db_session.commit()

    create_response = await client.post(
        '/api/admin/trades/',
        headers=admin_headers,
        json={
            'portfolio_id': portfolio.id,
            'asset_id': asset.id,
            'direction': 'buy',
            'quantity': '2',
            'price': '150.50',
            'trade_time': '2024-01-01T10:00:00Z',
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['portfolio_id'] == portfolio.id
    assert created['asset_id'] == asset.id
    assert created['direction'] == 'buy'
    assert Decimal(str(created['quantity'])) == Decimal('2')
    assert Decimal(str(created['price'])) == Decimal('150.50')
    assert created['trade_time'].startswith('2024-01-01T10:00:00')

    get_response = await client.get(
        f'/api/admin/trades/{created["id"]}',
        headers=admin_headers,
    )
    list_response = await client.get('/api/admin/trades/', headers=admin_headers)
    update_response = await client.patch(
        f'/api/admin/trades/{created["id"]}',
        headers=admin_headers,
        json={
            'quantity': '3',
            'price': '175.00',
        },
    )

    assert get_response.status_code == 200
    assert get_response.json() == created

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]['id'] == created['id']

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['id'] == created['id']
    assert Decimal(str(updated['quantity'])) == Decimal('3')
    assert Decimal(str(updated['price'])) == Decimal('175.00')

    delete_response = await client.delete(
        f'/api/admin/trades/{created["id"]}',
        headers=admin_headers,
    )
    deleted_get_response = await client.get(
        f'/api/admin/trades/{created["id"]}',
        headers=admin_headers,
    )

    assert delete_response.status_code == 204
    assert deleted_get_response.status_code == 404
    assert deleted_get_response.json() == {'detail': 'SZ trade not found'}


async def test_admin_trades_returns_404_for_missing_trade(
    client: AsyncClient,
) -> None:
    _, admin_headers = await auth_headers(
        client,
        name='Missing Trade Admin',
        email='missing-trade-admin@example.com',
        role='admin',
    )

    response = await client.get('/api/admin/trades/999', headers=admin_headers)

    assert response.status_code == 404
    assert response.json() == {'detail': 'SZ trade not found'}
