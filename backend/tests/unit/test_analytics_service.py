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
async def test_portfolio_snapshot_basic() -> None:
    portfolio = SimpleNamespace(id=1, user_id=7, name='Main', currency='RUB')
    trades = [
        SimpleNamespace(asset_id=1, direction='buy', quantity=Decimal('2'), price=Decimal('100')),
        SimpleNamespace(asset_id=1, direction='buy', quantity=Decimal('1'), price=Decimal('105')),
        SimpleNamespace(asset_id=1, direction='sell', quantity=Decimal('1'), price=Decimal('110')),
        SimpleNamespace(asset_id=2, direction='buy', quantity=Decimal('1'), price=Decimal('50')),
        SimpleNamespace(asset_id=3, direction='buy', quantity=Decimal('3'), price=Decimal('200')),
        SimpleNamespace(asset_id=3, direction='sell', quantity=Decimal('1'), price=Decimal('210')),
        SimpleNamespace(asset_id=4, direction='buy', quantity=Decimal('4'), price=Decimal('60')),
        SimpleNamespace(asset_id=4, direction='buy', quantity=Decimal('1'), price=Decimal('65')),
        SimpleNamespace(asset_id=4, direction='sell', quantity=Decimal('2'), price=Decimal('70')),
        SimpleNamespace(asset_id=5, direction='buy', quantity=Decimal('2'), price=Decimal('150')),
    ]
    prices = {
        1: Decimal('120'),
        2: Decimal('80'),
        3: Decimal('190'),
        4: Decimal('75'),
        5: Decimal('140'),
    }
    assets = [
        SimpleNamespace(id=1, ticker='SBER', full_name='Sberbank', sector='financials'),
        SimpleNamespace(id=2, ticker='LKOH', full_name='Lukoil', sector='oil_gas'),
        SimpleNamespace(id=3, ticker='YDEX', full_name='Yandex', sector='it'),
        SimpleNamespace(id=4, ticker='MGNT', full_name='Magnit', sector='consumer'),
        SimpleNamespace(id=5, ticker='PHOR', full_name='PhosAgro', sector='chemicals'),
    ]

    repo = FakeAnalyticsRepo(
        portfolio=portfolio,
        trades=trades,
        prices=prices,
        assets=assets,
    )
    service = AnalyticsService(repo=repo)

    response = await service.portfolio_snapshot(portfolio_id=1)

    assert response.portfolio_id == 1
    assert response.positions_count == 5
    assert response.market_value == Decimal('1205')
    assert response.cost_basis == Decimal('1140')
    assert response.unrealized_pnl == Decimal('65')
    assert response.unrealized_return_pct.quantize(Decimal('0.000001')) == Decimal('5.701754')
    assert [pos.ticker for pos in response.top_positions] == ['YDEX', 'PHOR', 'SBER']


@pytest.mark.asyncio
async def test_sector_distribution_basic() -> None:
    portfolio = SimpleNamespace(id=1, user_id=7, name='Main', currency='RUB')
    trades = [
        SimpleNamespace(asset_id=1, direction='buy', quantity=Decimal('2'), price=Decimal('100')),
        SimpleNamespace(asset_id=1, direction='buy', quantity=Decimal('1'), price=Decimal('105')),
        SimpleNamespace(asset_id=1, direction='sell', quantity=Decimal('1'), price=Decimal('110')),
        SimpleNamespace(asset_id=2, direction='buy', quantity=Decimal('2'), price=Decimal('150')),
        SimpleNamespace(asset_id=2, direction='sell', quantity=Decimal('1'), price=Decimal('160')),
        SimpleNamespace(asset_id=3, direction='buy', quantity=Decimal('1'), price=Decimal('300')),
        SimpleNamespace(asset_id=4, direction='buy', quantity=Decimal('3'), price=Decimal('200')),
        SimpleNamespace(asset_id=4, direction='sell', quantity=Decimal('1'), price=Decimal('210')),
    ]
    prices = {
        1: Decimal('120'),
        2: Decimal('170'),
        3: Decimal('320'),
        4: Decimal('190'),
    }
    assets = [
        SimpleNamespace(id=1, ticker='SBER', full_name='Sberbank', sector='financials'),
        SimpleNamespace(id=2, ticker='TCSG', full_name='TCS Group', sector='financials'),
        SimpleNamespace(id=3, ticker='LKOH', full_name='Lukoil', sector='oil_gas'),
        SimpleNamespace(id=4, ticker='YDEX', full_name='Yandex', sector='it'),
    ]

    repo = FakeAnalyticsRepo(
        portfolio=portfolio,
        trades=trades,
        prices=prices,
        assets=assets,
    )
    service = AnalyticsService(repo=repo)

    response = await service.sector_distribution(portfolio_id=1)

    by_sector = {position.sector: position for position in response.sectors}

    assert response.portfolio_id == 1
    assert response.market_value == Decimal('1110')
    assert set(by_sector) == {'financials', 'oil_gas', 'it'}
    assert by_sector['financials'].market_value == Decimal('410')
    assert by_sector['oil_gas'].market_value == Decimal('320')
    assert by_sector['it'].market_value == Decimal('380')
    assert by_sector['financials'].weight_percent.quantize(Decimal('0.000001')) == Decimal(
        '36.936937'
    )
    assert by_sector['oil_gas'].weight_percent.quantize(Decimal('0.000001')) == Decimal('28.828829')
    assert by_sector['it'].weight_percent.quantize(Decimal('0.000001')) == Decimal('34.234234')


@pytest.mark.asyncio
async def test_portfolio_snapshot_returns_empty_metrics_for_empty_portfolio() -> None:
    portfolio = SimpleNamespace(id=1, user_id=7, name='Main', currency='RUB')
    repo = FakeAnalyticsRepo(
        portfolio=portfolio,
        trades=[],
        prices={},
        assets=[],
    )
    service = AnalyticsService(repo=repo)

    response = await service.portfolio_snapshot(portfolio_id=1)

    assert response.portfolio_id == 1
    assert response.positions_count == 0
    assert response.market_value == Decimal('0')
    assert response.cost_basis == Decimal('0')
    assert response.unrealized_pnl == Decimal('0')
    assert response.unrealized_return_pct == Decimal('0')
    assert response.top_positions == []


@pytest.mark.asyncio
async def test_sector_distribution_for_empty_portfolio() -> None:
    portfolio = SimpleNamespace(id=1, user_id=7, name='Main', currency='RUB')
    repo = FakeAnalyticsRepo(
        portfolio=portfolio,
        trades=[],
        prices={},
        assets=[],
    )
    service = AnalyticsService(repo=repo)

    response = await service.sector_distribution(portfolio_id=1)

    assert response.portfolio_id == 1
    assert response.market_value == Decimal('0')
    assert response.sectors == []


@pytest.mark.asyncio
async def test_sector_distribution_for_closed_portfolio() -> None:
    portfolio = SimpleNamespace(id=1, user_id=7, name='Main', currency='RUB')
    trades = [
        SimpleNamespace(asset_id=1, direction='buy', quantity=Decimal('2'), price=Decimal('100')),
        SimpleNamespace(asset_id=1, direction='sell', quantity=Decimal('2'), price=Decimal('120')),
        SimpleNamespace(asset_id=2, direction='buy', quantity=Decimal('1'), price=Decimal('200')),
        SimpleNamespace(asset_id=2, direction='sell', quantity=Decimal('1'), price=Decimal('210')),
    ]
    repo = FakeAnalyticsRepo(
        portfolio=portfolio,
        trades=trades,
        prices={1: Decimal('120'), 2: Decimal('210')},
        assets=[
            SimpleNamespace(id=1, ticker='SBER', full_name='Sberbank', sector='financials'),
            SimpleNamespace(id=2, ticker='YDEX', full_name='Yandex', sector='it'),
        ],
    )
    service = AnalyticsService(repo=repo)

    response = await service.sector_distribution(portfolio_id=1)

    assert response.portfolio_id == 1
    assert response.market_value == Decimal('0')
    assert response.sectors == []


@pytest.mark.asyncio
async def test_sector_distribution_single_sector_portfolio() -> None:
    portfolio = SimpleNamespace(id=1, user_id=7, name='Main', currency='RUB')
    trades = [
        SimpleNamespace(asset_id=1, direction='buy', quantity=Decimal('2'), price=Decimal('100')),
        SimpleNamespace(asset_id=1, direction='sell', quantity=Decimal('1'), price=Decimal('110')),
        SimpleNamespace(asset_id=2, direction='buy', quantity=Decimal('2'), price=Decimal('150')),
        SimpleNamespace(asset_id=2, direction='sell', quantity=Decimal('1'), price=Decimal('160')),
    ]
    repo = FakeAnalyticsRepo(
        portfolio=portfolio,
        trades=trades,
        prices={1: Decimal('120'), 2: Decimal('170')},
        assets=[
            SimpleNamespace(id=1, ticker='SBER', full_name='Sberbank', sector='financials'),
            SimpleNamespace(id=2, ticker='TCSG', full_name='TCS Group', sector='financials'),
        ],
    )
    service = AnalyticsService(repo=repo)

    response = await service.sector_distribution(portfolio_id=1)

    assert response.portfolio_id == 1
    assert response.market_value == Decimal('290')
    assert len(response.sectors) == 1
    assert response.sectors[0].sector == 'financials'
    assert response.sectors[0].market_value == Decimal('290')
    assert response.sectors[0].weight_percent == Decimal('100')


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('method_name', 'kwargs'),
    [
        ('portfolio_snapshot', {'portfolio_id': 1}),
        ('portfolio_snapshot_for_user', {'portfolio_id': 1, 'user_id': 7}),
    ],
)
async def test_portfolio_snapshot_for_closed_portfolio(method_name: str, kwargs: dict) -> None:
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
