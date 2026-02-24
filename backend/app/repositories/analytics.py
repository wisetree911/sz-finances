from app.models.portfolio import Portfolio
from app.models.trade import Trade
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AssetRepositoryPostgres:
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
