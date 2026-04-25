from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services.analytics import AnalyticsService


class FakeAnalyticsRepo:
    def __init__(self, *, portfolio, trades, prices, assets):
        self._portfolio = portfolio
        self._trades = trades
        self._prices = prices
        self._assets = assets

    async def get_portfolio(self, portfolio_id: int):
        return self._portfolio

    async def get_trades_by_portfolio_id(self, portfolio_id: int):
        return self._trades

    async def get_prices_dict_by_ids(self, asset_ids):
        return self._prices

    async def get_assets_by_ids(self, asset_ids):
        return self._assets


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('method_name', 'kwargs'),
    [
        ('portfolio_snapshot', {'portfolio_id': 1}),
        ('portfolio_snapshot_for_user', {'portfolio_id': 1, 'user_id': 7}),
    ],
)
async def test_portfolio_snapshot_returns_empty_metrics_for_fully_closed_portfolio(
    method_name: str, kwargs: dict
) -> None:
    portfolio = SimpleNamespace(id=1, user_id=7, name='Main', currency='RUB')
    trades = [
        SimpleNamespace(
            asset_id=1,
            direction='buy',
            quantity=Decimal('1'),
            price=Decimal('100'),
        ),
        SimpleNamespace(
            asset_id=1,
            direction='sell',
            quantity=Decimal('1'),
            price=Decimal('120'),
        ),
    ]
    repo = FakeAnalyticsRepo(
        portfolio=portfolio,
        trades=trades,
        prices={1: Decimal('120')},
        assets=[
            SimpleNamespace(id=1, ticker='SBER', full_name='Sberbank', sector='financials'),
        ],
    )
    service = AnalyticsService(repo=repo)

    response = await getattr(service, method_name)(**kwargs)

    assert response.portfolio_id == 1
    assert response.positions_count == 0
    assert response.market_value == Decimal('0')
    assert response.cost_basis == Decimal('0')
    assert response.unrealized_pnl == Decimal('0')
    assert response.unrealized_return_pct == Decimal('0')
    assert response.top_positions == []
