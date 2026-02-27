from collections.abc import Sequence
from decimal import Decimal

from app.models.asset import Asset
from app.models.asset_price import AssetPrice
from app.models.portfolio import Portfolio
from app.models.trade import Trade
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_portfolio(self, portfolio_id: int):
        query = select(Portfolio).where(Portfolio.id == portfolio_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_trades_by_portfolio_id(self, portfolio_id: int):
        query = select(Trade).where(Trade.portfolio_id == portfolio_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_prices_dict_by_ids(self, asset_ids: list[int]) -> dict[int, Decimal]:
        query = (
            select(AssetPrice.asset_id, AssetPrice.price)
            .distinct(AssetPrice.asset_id)
            .where(AssetPrice.asset_id.in_(asset_ids))
            .order_by(AssetPrice.asset_id, AssetPrice.timestamp.desc())
        )
        result = await self.session.execute(query)
        rows = result.all()
        return {asset_id: price for asset_id, price in rows}

    async def get_assets_by_ids(self, ids: list[int]) -> Sequence[Asset]:
        query = select(Asset).where(Asset.id.in_(ids))
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return rows
