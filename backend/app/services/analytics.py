from typing import List, Dict
from datetime import datetime, timedelta
from shared.repositories.asset_price import AssetPriceRepository
from shared.repositories.portfolio import PortfolioRepository
from shared.repositories.asset import AssetRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.schemas.analytics import PortfolioShapshotResponse, TopPosition, SectorDistributionResponse, SectorPosition, PortfolioPrice, PortfolioDynamicsResponse
from shared.repositories.trade import TradeRepository
from app.analytics.models import PortfolioPositionPrepared, Lot, TradeDTO, SectorPositionAn
from app.analytics.analytics_calc import calc_unrealized_pnl, build_only_buy_positions, calc_cost_basis, calc_market_value, calc_unrealized_return_pct, build_sector_positions

# убрать всю аналитику отсюлаёёда
class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session=session
        self.asset_price_repo=AssetPriceRepository(session=session)
        self.portfolio_repo=PortfolioRepository(session=session)
        self.asset_repo=AssetRepository(session=session)
        self.trade_repo=TradeRepository(session=session)

    async def portfolio_snapshot(self, portfolio_id: int) -> PortfolioShapshotResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None: raise HTTPException(404, "SZ portfolio not found")
        portfolio_trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        if not portfolio_trades:
            return PortfolioShapshotResponse.empty(portfolio)
        asset_ids = {trade.asset_id for trade in portfolio_trades}
        asset_market_prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)
        trade_dtos = [TradeDTO.from_orm(trade) for trade in portfolio_trades]

        assets = await self.asset_repo.get_assets_by_ids(asset_ids)
        portfolio_positions: List[PortfolioPositionPrepared] = build_only_buy_positions(trades=trade_dtos, current_prices=asset_market_prices, assets=assets)
        cost_basis = calc_cost_basis(asset_positive_positons=portfolio_positions)
        unrealized_pnl = calc_unrealized_pnl(asset_positive_positons=portfolio_positions)
        market_price = calc_market_value(asset_positive_positons=portfolio_positions)

        top_positions = [
            TopPosition(
                    asset_id=pos.asset_id,
                    ticker=pos.ticker,
                    full_name=pos.name,
                    quantity=pos.quantity,
                    avg_buy_price=pos.mid_price,
                    asset_market_price=pos.asset_market_price,
                    market_value=pos.market_price,
                    unrealized_pnl=pos.unrealized_pnl,
                    unrealized_return_pct=pos.unrealized_return_pct,
                    weight_pct=pos.market_price / market_price * 100
                ) for pos in sorted(portfolio_positions, key=lambda pos: pos.market_price / market_price * 100, reverse=True)[:5]
        ]

        return PortfolioShapshotResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=market_price,
            unrealized_pnl=unrealized_pnl,
            unrealized_return_pct=calc_unrealized_return_pct(unrealized_pnl=unrealized_pnl, cost_basis=cost_basis),
            cost_basis=cost_basis,
            currency=portfolio.currency,
            positions_count=len(portfolio_positions),
            top_positions=top_positions
        )

    async def sector_distribution(self, portfolio_id: int) -> SectorDistributionResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None: raise HTTPException(404, "SZ portfolio not found")
        portfolio_trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        if not portfolio_trades:
            return SectorDistributionResponse.empty(portfolio)
        asset_ids = {trade.asset_id for trade in portfolio_trades}
        market_prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)
        assets = await self.asset_repo.get_assets_by_ids(asset_ids)
        trade_dtos = [TradeDTO.from_orm(trade) for trade in portfolio_trades]
        sector_positions: List[SectorPositionAn] = build_sector_positions(trades=trade_dtos, current_prices=market_prices, assets=assets)
        portfolio_market_value = sum(pos.market_value for pos in sector_positions)

        secs: List[SectorPosition] = [
            SectorPosition(
                sector=pos.sector, 
                market_value=pos.market_value, 
                weight_percent=pos.market_value / portfolio_market_value * 100
            ) for pos in sector_positions]

        return SectorDistributionResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=portfolio_market_value,
            currency=portfolio.currency,
            sectors=secs
        ) 
    

#     async def portfolio_dynamics_for_24h(self, portfolio_id: int) -> PortfolioDynamicsResponse:
#         portfolio = await self.portfolio_repo.get_by_id(portfolio_id=portfolio_id)
#         if portfolio is None:
#             raise HTTPException(404, "SZ portfolio not found")
#         positions = await self.portfolio_position_repo.get_by_portfolio_id(portfolio_id=portfolio_id)
#         if not positions:
#             return PortfolioDynamicsResponse.empty(portfolio=portfolio)

#         timestamp_now = datetime.utcnow()
#         asset_ids = [pos.asset_id for pos in positions]

#         asset_prices = await self.asset_price_repo.get_prices_since(ids=asset_ids, since=timestamp_now - timedelta(days=1) )
        
#         timestamps_count = get_timestamps_count_24h(ts_now=timestamp_now)
#         time_series = get_sorted_timeseries_24h(ts_now=timestamp_now, count=timestamps_count)
#         asset_id_to_quantity = {}
#         for pos in positions:
#             asset_id_to_quantity[pos.asset_id] = pos.quantity
#         data = []
#         for ts in time_series:
#             data.append(PortfolioPrice(timestamp=ts, total_value=get_portfolio_price_by_ts(ts, asset_prices, asset_id_to_quantity)))
        
#         return PortfolioDynamicsResponse(
#             portfolio_id=portfolio.id,
#             name=portfolio.name,
#             data=data
#         )