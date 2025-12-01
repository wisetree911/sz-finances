from datetime import datetime, timedelta
from locale import currency
from turtle import position
from shared.repositories.asset_price import AssetPriceRepository
from shared.repositories.portfolio import PortfolioRepository
from shared.repositories.asset import AssetRepository
from shared.repositories.portfolio_position import PortfolioPositionRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.schemas.analytics import PortfolioShapshotResponse, TopPosition
class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session=session
        self.asset_price_repo=AssetPriceRepository(session=session)
        self.portfolio_repo=PortfolioRepository(session=session)
        self.portfolio_position_repo=PortfolioPositionRepository(session=session)
        self.asset_repo=AssetRepository(session=session)

    async def portfolio_snapshot(self, portfolio_id: int): # добавить округление и реально выводить топ три позиции и получать реально последние цены
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id=portfolio_id)
        positions = await self.portfolio_position_repo.get_by_portfolio_id(portfolio_id)
        tops=list()
        if not positions: raise HTTPException(404, "SZ no positions were found")
        total_value = int()
        asset_ids=[pos.asset_id for pos in positions]
        prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)
        
        total_value = sum(pos.quantity * prices[pos.asset_id] for pos in positions)
        invested_value = sum([pos.avg_price * pos.quantity for pos in positions])
        total_profit = total_value - invested_value
        total_profit_percent = total_profit / invested_value * 100
        positions_count=len(positions)
        assets = await self.asset_repo.get_assets_dict_by_ids(asset_ids)
        for pos in positions:
            new_top = TopPosition(
                asset_id=pos.asset_id,
                ticker=assets[pos.asset_id].ticker,
                full_name=assets[pos.asset_id].full_name,
                quantity=pos.quantity,
                avg_buy_price=pos.avg_price,
                current_price=prices[pos.asset_id],
                current_value=pos.quantity * prices[pos.asset_id],
                profit=pos.quantity * prices[pos.asset_id] - pos.quantity * pos.avg_price,
                profit_percent = ((prices[pos.asset_id] - pos.avg_price) / pos.avg_price) * 100
            )
            tops.append(new_top)

        

        return PortfolioShapshotResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            total_value=total_value,
            total_profit=total_profit,
            total_profit_percent=total_profit_percent,
            invested_value=invested_value,
            currency=portfolio.currency,
            positions_count=positions_count,
            top_positions= tops
        )
    


    
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