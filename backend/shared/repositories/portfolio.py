from sqlalchemy import select
from shared.models.portfolio import Portfolio
from sqlalchemy.ext.asyncio import AsyncSession
class PortfolioRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_id(self, portfolio_id: int):
        query = select(Portfolio).where(Portfolio.id == portfolio_id)
        result = await self.session.execute(query)
        portfolio = result.scalar_one_or_none()
        return portfolio
    
    async def get_all(self):
        query = select(Portfolio)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, user_id: int, name: str):
        new_portfolio = Portfolio(
            user_id=user_id,
            name=name
        )
        self.session.add(new_portfolio)
        await self.session.commit()
        await self.session.refresh(new_portfolio)
        return new_portfolio
    
    async def delete(self, portfolio: Portfolio):
        await self.session.delete(portfolio)
        await self.session.commit()

    async def get_by_user_id(self, user_id: int):
        query = select(Portfolio).where(Portfolio.user_id == user_id)
        result = await self.session.execute(query)
        portfolios = result.scalars().all()
        return portfolios
    

