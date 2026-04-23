from decimal import Decimal
from types import SimpleNamespace

from app.analytics.analytics_calc import (
    build_dynamics_positions,
    build_remaining_buy_lots_fifo,
    calc_cost_basis,
    calc_market_value,
    calc_unrealized_pnl,
)
from app.analytics.models import TradeDTO


def test_build_remaining_buy_lots_fifo_keeps_only_open_lots() -> None:
    trades = [
        TradeDTO(asset_id=1, direction='buy', quantity=Decimal('2'), price=Decimal('10')),
        TradeDTO(asset_id=1, direction='buy', quantity=Decimal('3'), price=Decimal('20')),
        TradeDTO(asset_id=1, direction='sell', quantity=Decimal('4'), price=Decimal('30')),
    ]
    current_prices = {1: Decimal('25')}
    assets = [
        SimpleNamespace(id=1, ticker='SBER', full_name='Sberbank', sector='financials'),
    ]

    positions = build_remaining_buy_lots_fifo(trades, current_prices, assets)

    assert len(positions) == 1
    assert positions[0].asset_id == 1
    assert positions[0].quantity == Decimal('1')
    assert positions[0].cost_basis == Decimal('20')
    assert positions[0].market_price == Decimal('25')


def test_portfolio_metric_helpers_calculate_from_open_positions() -> None:
    trades = [
        TradeDTO(asset_id=1, direction='buy', quantity=Decimal('1'), price=Decimal('100')),
        TradeDTO(asset_id=1, direction='buy', quantity=Decimal('2'), price=Decimal('110')),
    ]
    current_prices = {1: Decimal('120')}
    assets = [
        SimpleNamespace(id=1, ticker='GAZP', full_name='Gazprom', sector='oil_gas'),
    ]

    positions = build_remaining_buy_lots_fifo(trades, current_prices, assets)

    assert calc_cost_basis(positions) == Decimal('320')
    assert calc_market_value(positions) == Decimal('360')
    assert calc_unrealized_pnl(positions) == Decimal('40')


def test_build_dynamics_positions_returns_net_quantity_per_asset() -> None:
    trades = [
        TradeDTO(asset_id=1, direction='buy', quantity=Decimal('5'), price=Decimal('10')),
        TradeDTO(asset_id=1, direction='sell', quantity=Decimal('2'), price=Decimal('12')),
        TradeDTO(asset_id=2, direction='buy', quantity=Decimal('3'), price=Decimal('20')),
    ]

    positions = build_dynamics_positions(trades)
    by_asset_id = {position.asset_id: position.quantity for position in positions}

    assert by_asset_id == {
        1: Decimal('3'),
        2: Decimal('3'),
    }
