from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from app.infrastructure.redis.deps import get_cache
from app.main import app
from app.models.asset import Asset
from app.models.asset_price import AssetPrice
from app.models.portfolio import Portfolio
from app.models.trade import Trade
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class InMemoryCache:
    def __init__(self) -> None:
        self._items: dict[str, Any] = {}

    async def get_json(self, key: str) -> Any | None:
        return self._items.get(key)

    async def set_json(self, key: str, payload: Any, *, ttl: int) -> None:
        self._items[key] = payload

    async def delete(self, key: str) -> None:
        self._items.pop(key, None)


@pytest.fixture(autouse=True)
def override_cache() -> Iterator[None]:
    app.dependency_overrides[get_cache] = lambda: InMemoryCache()
    yield
    app.dependency_overrides.pop(get_cache, None)


def as_decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def make_trade(
    *,
    portfolio_id: int,
    asset_id: int,
    direction: str,
    quantity: Decimal,
    price: Decimal,
) -> Trade:
    return Trade(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        direction=direction,
        quantity=quantity,
        price=price,
        trade_time=datetime.now(UTC),
    )


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


async def create_asset_with_price(
    db_session: AsyncSession,
    *,
    ticker: str,
    full_name: str,
    sector: str,
    price: Decimal,
) -> Asset:
    asset = Asset(ticker=ticker, full_name=full_name, type='stock', sector=sector)
    db_session.add(asset)
    await db_session.flush()

    db_session.add(
        AssetPrice(
            asset_id=asset.id,
            price=price,
            currency='RUB',
            source='test',
        )
    )
    return asset


async def test_portfolio_snapshot_returns_metrics_for_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user, headers = await auth_headers(
        client,
        name='Analytics User',
        email='analytics@example.com',
    )

    portfolio = Portfolio(user_id=user['id'], name='Main', currency='RUB')
    db_session.add(portfolio)
    await db_session.flush()

    sber = await create_asset_with_price(
        db_session,
        ticker='SBER',
        full_name='Sberbank',
        sector='financials',
        price=Decimal('120'),
    )
    lkoh = await create_asset_with_price(
        db_session,
        ticker='LKOH',
        full_name='Lukoil',
        sector='oil_gas',
        price=Decimal('80'),
    )
    ydex = await create_asset_with_price(
        db_session,
        ticker='YDEX',
        full_name='Yandex',
        sector='it',
        price=Decimal('190'),
    )
    phor = await create_asset_with_price(
        db_session,
        ticker='PHOR',
        full_name='PhosAgro',
        sector='chemicals',
        price=Decimal('140'),
    )

    db_session.add_all(
        [
            make_trade(
                portfolio_id=portfolio.id,
                asset_id=sber.id,
                direction='buy',
                quantity=Decimal('2'),
                price=Decimal('100'),
            ),
            make_trade(
                portfolio_id=portfolio.id,
                asset_id=lkoh.id,
                direction='buy',
                quantity=Decimal('1'),
                price=Decimal('50'),
            ),
            make_trade(
                portfolio_id=portfolio.id,
                asset_id=ydex.id,
                direction='buy',
                quantity=Decimal('3'),
                price=Decimal('200'),
            ),
            make_trade(
                portfolio_id=portfolio.id,
                asset_id=phor.id,
                direction='buy',
                quantity=Decimal('2'),
                price=Decimal('90'),
            ),
        ]
    )
    await db_session.commit()

    response = await client.get(
        f'/api/analytics/{portfolio.id}/snapshot',
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload['portfolio_id'] == portfolio.id
    assert payload['name'] == 'Main'
    assert payload['currency'] == 'RUB'
    assert payload['positions_count'] == 4
    assert as_decimal(payload['market_value']) == Decimal('1170')
    assert as_decimal(payload['cost_basis']) == Decimal('1030')
    assert as_decimal(payload['unrealized_pnl']) == Decimal('140')
    assert as_decimal(payload['unrealized_return_pct']).quantize(Decimal('0.000001')) == Decimal(
        '13.592233'
    )
    assert [position['ticker'] for position in payload['top_positions']] == [
        'YDEX',
        'PHOR',
        'SBER',
    ]
    assert as_decimal(payload['top_positions'][0]['market_value']) == Decimal('570')
    assert as_decimal(payload['top_positions'][0]['unrealized_pnl']) == Decimal('-30')


async def test_portfolio_snapshot_returns_empty_metrics_for_empty_portfolio(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user, headers = await auth_headers(
        client,
        name='Empty Portfolio User',
        email='empty@example.com',
    )
    portfolio = Portfolio(user_id=user['id'], name='Cash', currency='RUB')
    db_session.add(portfolio)
    await db_session.commit()

    response = await client.get(
        f'/api/analytics/{portfolio.id}/snapshot',
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload['portfolio_id'] == portfolio.id
    assert payload['positions_count'] == 0
    assert as_decimal(payload['market_value']) == Decimal('0')
    assert as_decimal(payload['cost_basis']) == Decimal('0')
    assert as_decimal(payload['unrealized_pnl']) == Decimal('0')
    assert as_decimal(payload['unrealized_return_pct']) == Decimal('0')
    assert payload['top_positions'] == []


async def test_portfolio_snapshot_returns_empty_metrics_for_fully_closed_portfolio(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user, headers = await auth_headers(
        client,
        name='Closed Portfolio User',
        email='closed@example.com',
    )
    portfolio = Portfolio(user_id=user['id'], name='Closed', currency='RUB')
    db_session.add(portfolio)
    await db_session.flush()

    sber = await create_asset_with_price(
        db_session,
        ticker='SBER',
        full_name='Sberbank',
        sector='financials',
        price=Decimal('120'),
    )
    db_session.add_all(
        [
            make_trade(
                portfolio_id=portfolio.id,
                asset_id=sber.id,
                direction='buy',
                quantity=Decimal('1'),
                price=Decimal('100'),
            ),
            make_trade(
                portfolio_id=portfolio.id,
                asset_id=sber.id,
                direction='sell',
                quantity=Decimal('1'),
                price=Decimal('120'),
            ),
        ]
    )
    await db_session.commit()

    response = await client.get(
        f'/api/analytics/{portfolio.id}/snapshot',
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload['portfolio_id'] == portfolio.id
    assert payload['positions_count'] == 0
    assert as_decimal(payload['market_value']) == Decimal('0')
    assert as_decimal(payload['cost_basis']) == Decimal('0')
    assert as_decimal(payload['unrealized_pnl']) == Decimal('0')
    assert as_decimal(payload['unrealized_return_pct']) == Decimal('0')
    assert payload['top_positions'] == []


async def test_portfolio_snapshot_returns_404_for_foreign_portfolio(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    owner = await register_user(
        client,
        name='Owner User',
        email='owner@example.com',
    )
    _, headers = await auth_headers(
        client,
        name='Another User',
        email='another@example.com',
    )

    portfolio = Portfolio(user_id=owner['id'], name='Private', currency='RUB')
    db_session.add(portfolio)
    await db_session.commit()

    response = await client.get(
        f'/api/analytics/{portfolio.id}/snapshot',
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'SZ portfolio not found'}


async def test_admin_snapshot_returns_metrics_for_any_portfolio(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    owner = await register_user(
        client,
        name='Portfolio Owner',
        email='portfolio-owner@example.com',
    )
    _, admin_headers = await auth_headers(
        client,
        name='Admin User',
        email='admin@example.com',
        role='admin',
    )

    portfolio = Portfolio(user_id=owner['id'], name='Admin Visible', currency='RUB')
    db_session.add(portfolio)
    await db_session.flush()

    sber = await create_asset_with_price(
        db_session,
        ticker='SBER',
        full_name='Sberbank',
        sector='financials',
        price=Decimal('120'),
    )
    db_session.add(
        make_trade(
            portfolio_id=portfolio.id,
            asset_id=sber.id,
            direction='buy',
            quantity=Decimal('2'),
            price=Decimal('100'),
        )
    )
    await db_session.commit()

    response = await client.get(
        f'/api/admin/analytics/{portfolio.id}/snapshot',
        headers=admin_headers,
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload['portfolio_id'] == portfolio.id
    assert payload['positions_count'] == 1
    assert as_decimal(payload['market_value']) == Decimal('240')
    assert as_decimal(payload['cost_basis']) == Decimal('200')
    assert as_decimal(payload['unrealized_pnl']) == Decimal('40')
    assert [position['ticker'] for position in payload['top_positions']] == ['SBER']


async def test_admin_snapshot_requires_admin_role(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    owner = await register_user(
        client,
        name='Regular Owner',
        email='regular-owner@example.com',
    )
    _, user_headers = await auth_headers(
        client,
        name='Regular User',
        email='regular-user@example.com',
    )

    portfolio = Portfolio(user_id=owner['id'], name='Protected', currency='RUB')
    db_session.add(portfolio)
    await db_session.commit()

    response = await client.get(
        f'/api/admin/analytics/{portfolio.id}/snapshot',
        headers=user_headers,
    )

    assert response.status_code == 403
    assert response.json() == {'detail': 'Admin privileges required'}


async def test_admin_snapshot_returns_404_for_missing_portfolio(
    client: AsyncClient,
) -> None:
    _, admin_headers = await auth_headers(
        client,
        name='Missing Portfolio Admin',
        email='missing-admin@example.com',
        role='admin',
    )

    response = await client.get(
        '/api/admin/analytics/999/snapshot',
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'SZ portfolio not found'}
