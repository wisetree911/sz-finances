from shared.repositories.portfolio import PortfolioRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

class PortfolioService:
     def __init__(self, session):
        self.session = session
        self.repo = PortfolioRepository(session=session)

     async def get_all_portfolios(self):
        return await self.repo.get_all()
    
     async def get_portfolio_by_portfolio_id(self, portfolio_id: int):
        portfolio = await self.repo.get_by_id(portfolio_id=portfolio_id)
        if portfolio is None:
            raise HTTPException(404, "SZ portfolio not found")
        return portfolio
    
     async def create_portfolio(self, portfolio_schema):
        return await self.repo.create(
            user_id=portfolio_schema.user_id,
            name=portfolio_schema.name
        )
    
     async def delete_portfolio_by_portfolio_id(self, portfolio_id: int):
        portfolio = await self.repo.get_by_id(portfolio_id=portfolio_id)
        if portfolio is None:
            raise HTTPException(404, "SZ portfolio not found")
        
        await self.repo.delete(portfolio=portfolio)
    
     async def get_user_portfolios(self, user_id: int):
        return await self.repo.get_by_user_id(user_id=user_id)

