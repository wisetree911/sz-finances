from datetime import datetime, timedelta
from shared.repositories.asset_price import AssetPriceRepository
from shared.repositories.portfolio import PortfolioRepository
from shared.repositories.portfolio_position import PortfolioPositionRepository
from sqlalchemy.ext.asyncio import AsyncSession

class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session=session
        self.asset_price_repo=AssetPriceRepository(session=session)
        self.portfolio_repo=PortfolioRepository(session=session)
        self.portfolio_position_repo=PortfolioPositionRepository(session=session)
        
    async def portfolio_snapshot(self, portfolio_id: int):
        portfolio_positions = self.portfolio_position_repo.get_by_portfolio_id(portfolio_id=portfolio_id)
        total_value = 0
        for pos in portfolio_positions:
            total_value += self.asset_price_repo.get_by_id

        # get total_value_invested
        # total_money_now = sum[pos.asset_id.get_current_price() for pos in get_portfolio_positions_by_portfolio_id]
        # total_money_invested = sum[pos.avg_price * pos.quantity for pos in get_portfolio_positions_by_portfolio_id]
        # total_profit = total_money_now - total_money_invested 
        # total_profit_percent = total_profit / total_money_invested * 100
        # top3 = get_portfolio_positions.sort(by quantity * avg_price desc)
        # total_value + total_invested + total_profit + total_profit_percent for each of 3 positions

    async def sector_distribution(self, portfolio_id):
        pass

    async def positions_breakdown(self, portfolio_id):
        pass
    

    async def portfolios_dynamics(self, user_id: int):
        portfolios = await self.portfolio_repo.get_by_user_id(user_id=user_id)
        since = datetime.utcnow() - timedelta(hours=24)
        response = []
        for portfolio in portfolios:
            positions = await self.portfolio_position_repo.get_by_portfolio_id(portfolio_id=portfolio.id)
            if not positions:
                response.append({"id": portfolio.id, "name": portfolio.name, "data": []})
                continue

            asset_ids = [p.asset_id for p in positions]
            pos_dict = {p.asset_id: p.quantity for p in positions}

            prices = await self.asset_price_repo.get_prices_since(ids=asset_ids, since=since)

            time_map = {}
            for price in prices:
                ts = price.timestamp
                asset_id = price.asset_id
                if ts not in time_map: time_map[ts] = 0
                time_map[ts] += price.price * pos_dict[asset_id]
            
            data = [{"timestamp": ts.isoformat(), "value": float(val)}
                    for ts, val in sorted(time_map.items(), key=lambda x: x[0])
            ]
            
            response.append({
                "id" : portfolio.id,
                "name" : portfolio.name,
                "data" : data
            })
            
        return response


# {
#   "portfolio_id": 12,
#   "name": "Основной портфель",
#   "total_value": 512345.67, -> portfolio_positions.quantity * assets.asset_id.price
#   "total_profit": 12345.67, -> portfolio_positions.quantity * assets.asset_id.price - total_value 
#   "total_profit_percent": 2.47, 

#   "invested_value": 500000.00, -> portfolio_positions.avg_price * portfolio_positions.quantity

#   "currency": "RUB",

#   "positions_count": 8, count_rows with portfolio_id = !

#   "top_positions": [
#     {
#       "asset_id": 1,
#       "ticker": "GAZP",
#       "full_name": "ПАО Газпром",
#       "quantity": 40,
#       "avg_buy_price": 152.95,
#       "current_price": 163.50,
#       "current_value": 6540.00,
#       "profit": 420.00,
#       "profit_percent": 6.86
#     },
#     {
#       "asset_id": 2,
#       "ticker": "SBER",
#       "full_name": "Сбербанк",
#       "quantity": 75,
#       "avg_buy_price": 287.86,
#       "current_price": 305.10,
#       "current_value": 22882.50,
#       "profit": 1293.00,
#       "profit_percent": 5.99
#     }
#   ]
# }