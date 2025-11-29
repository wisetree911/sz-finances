from requests import session
from shared.repositories.asset import AssetRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

class AssetService:
    def __init__(self, session: AsyncSession):
        self.session=session
        self.repo=AssetRepository(session=session)

    async def get_all(self):
        return await self.repo.get_all()
    
    async def get_by_id(self, asset_id: int):
        asset = await self.repo.get_by_id(asset_id=asset_id)
        if asset is None:
            raise HTTPException(404, "SZ asset not found")
        return asset
    
    async def get_by_ticker(self, ticker: str):
        asset = await self.repo.get_by_ticker(ticker=ticker)
        if asset is None:
            raise HTTPException(404, "SZ asset not found")
        return asset
    
    async def create(self, asset_schema):
        return await self.repo.create(
                                             ticker=asset_schema.ticker, 
                                             full_name=asset_schema.full_name,
                                             type=asset_schema.type
                                             )

    async def delete(self, asset_id: int):
        asset = await self.repo.get_by_id(asset_id=asset_id)
        if asset is None:
            raise HTTPException(404, "SZ asset not found")
        
        await self.repo.delete(asset=asset)
    
    async def update(self, asset_id: int, data: dict):
        asset = await self.repo.get_by_id(asset_id=asset_id)
        if asset is None:
            raise HTTPException(404, "SZ asset not found")
        await self.repo.update(asset=asset, data=data)
        return asset