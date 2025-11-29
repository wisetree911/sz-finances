from requests import session
from sqlalchemy import select
from shared.models.asset import Asset
from sqlalchemy.ext.asyncio import AsyncSession

class AssetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, asset_id: int):
        query = select(Asset).where(Asset.id == asset_id)
        result = await self.session.execute(query)
        asset = result.scalar_one_or_none()
        return asset
    
    async def get_all(self):
        query = select(Asset)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_ticker(self, ticker: str):
        query = select(Asset).where(Asset.ticker == ticker)
        result = await self.session.execute(query)
        asset = result.scalar_one_or_none()
        return asset
    
    async def create(self, ticker: str, full_name: str, type: str):
        new_asset = Asset(
            ticker=ticker, 
            full_name=full_name,
            type=type
            )
        self.session.add(new_asset)
        await self.session.commit()
        await self.session.refresh(new_asset)
        return new_asset
    
    async def delete(self, asset: Asset):
        await self.session.delete(asset)
        await self.session.commit()

    
    async def update(self, asset: Asset, data: dict):
        for field, value in data.items():
            setattr(asset, field, value)
        await self.session.commit()
        await self.session.refresh(asset)
        return asset
    