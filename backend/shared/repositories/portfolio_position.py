from sqlalchemy import select
from shared.models.portfolio_position import PortfolioPosition
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.portfolio_position import PortfolioPositionUpdate, PortfolioPositionCreate
class PortfolioPositionRepository:
    def __init__(self, session: AsyncSession):
        self.session=session

    async def get_by_id(self, portflio_position_id: int):
        query = select(PortfolioPosition).where(PortfolioPosition.id == portflio_position_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self):
        query = select(PortfolioPosition)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, obj_in: PortfolioPositionCreate):
        obj = PortfolioPosition(**obj_in.dict())
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, portfolio_position: PortfolioPosition, obj_in: PortfolioPositionUpdate):
        update_data=obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(portfolio_position, field, value)
        await self.session.commit()
        await self.session.refresh(portfolio_position)
        return portfolio_position

    async def delete(self, portfolio_position: PortfolioPosition):
        await self.session.delete(portfolio_position)
        await self.session.commit()

    async def get_by_portfolio_id(self, portfolio_id):
        query = select(PortfolioPosition).where(PortfolioPosition.portfolio_id == portfolio_id)
        portfolio_positions = await self.session.execute(query)
        return portfolio_positions.scalars().all()
