from typing import List, Dict
from datetime import datetime, timedelta
from shared.models.asset_price import AssetPrice
from shared.repositories.asset_price import AssetPriceRepository
from shared.repositories.portfolio import PortfolioRepository
from shared.repositories.asset import AssetRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.schemas.analytics import PortfolioShapshotResponse, TopPosition, SectorDistributionResponse, SectorPosition, PortfolioPrice, PortfolioDynamicsResponse
# from app.analytics.portfolio_snapshot import get_asset_id_to_quantity_dict, calc_market_value
from shared.repositories.trade import TradeRepository
from app.analytics.models import AssetPosition, Lot, TradeDTO
from app.analytics.analytics_calc import calc_unrealized_pnl, build_only_buy_positions, calc_cost_basis, calc_market_value, calc_unrealized_return_pct

# убрать всю аналитику отсюлаёёда
class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session=session
        self.asset_price_repo=AssetPriceRepository(session=session)
        self.portfolio_repo=PortfolioRepository(session=session)
        self.asset_repo=AssetRepository(session=session)
        self.trade_repo=TradeRepository(session=session)

    async def get_portfolio_total_price(self, portfolio_id: int):

        trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id=portfolio_id)
        total_value = 0
        for trade in trades:
            if trade.direction == "buy":
                total_value += trade.quantity * trade.price
            elif trade.direction == "sell":
                total_value -= trade.quantity * trade.price
        return total_value

    async def portfolio_snapshot(self, portfolio_id: int):
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        asset_ids = {trade.asset_id for trade in trades}
        current_prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)

        trade_dtos = [TradeDTO.from_orm(trade) for trade in trades]
        positions = build_only_buy_positions(trades=trade_dtos)
        cost_basis = calc_cost_basis(asset_positive_positons=positions)
        unrealized_pnl = calc_unrealized_pnl(asset_positive_positons=positions, asset_prices=current_prices)

        top_positions = []

        for asset_id in asset_ids:
            top_positions.append(
                TopPosition(
                    asset_id=0,
                    ticker="none", # достать из ассет репо по asset_ids все данные и оттуда тикеры
                    full_name="none",  # достать из ассет репо по asset_ids все данные и оттуда имена
                    quantity=0, # все закрыто внутри модуля аналитики
                    avg_buy_price=0, # все закрыто внутри модуля аналитики
                    current_price=0, # достать из current_prices
                    current_value=0, # все закрыто внутри модуля аналитики + достать из current_prices
                    profit=0, # все закрыто внутри модуля аналитики + достать из current_prices
                    profit_percent=0, # все закрыто внутри модуля аналитики + достать из current_prices
                    weight_percent=0 # все закрыто внутри модуля аналитики + достать из current_prices
                )
            )

        return PortfolioShapshotResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=calc_market_value(asset_positive_positons=positions, asset_prices=current_prices),
            unrealized_pnl=unrealized_pnl,
            unrealized_return_pct=calc_unrealized_return_pct(unrealized_pnl=unrealized_pnl, cost_basis=cost_basis),
            cost_basis=cost_basis ,
            currency=portfolio.currency,
            positions_count=len(positions),
            top_positions=top_positions
        )

#     async def sector_distribution(self, portfolio_id: int) -> SectorDistributionResponse:
#         portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
#         if portfolio is None:
#             raise HTTPException(404, "SZ portfolio not found")
#         positions = await self.portfolio_position_repo.get_by_portfolio_id(portfolio_id)
#         if not positions:
#             return SectorDistributionResponse.empty(portfolio)
#         asset_ids=[pos.asset_id for pos in positions]
#         prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)
#         total_value = sum(pos.quantity * prices[pos.asset_id] for pos in positions)
#         assets = await self.asset_repo.get_assets_dict_by_ids(asset_ids)
#         sector_to_value={}
#         for pos in positions:
#             sec=assets[pos.asset_id].sector
#             value=prices[pos.asset_id] * pos.quantity
#             sector_to_value[sec]  = sector_to_value.get(sec, 0) + value
#         sector_positions = []
#         for sector in sector_to_value.keys():
#             sector_positions.append(SectorPosition(sector=sector, 
#                             current_value=sector_to_value[sector], 
#                             weight_percent=(sector_to_value[sector]/total_value)*100))
#         sector_positions.sort(key=lambda x: x.current_value, reverse=True)
#         return SectorDistributionResponse(
#             portfolio_id=portfolio.id,
#             name=portfolio.name,
#             total_value=total_value,
#             currency=portfolio.currency,
#             sectors=sector_positions
#         )


#     async def positions_breakdown(self, portfolio_id):
#         pass
    

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