from sqlalchemy import select
from app.models.asset_price import AssetPrice

class AssetPriceRepository:
    @staticmethod
    async def get_all(session):
        query = select(AssetPrice)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_assert_id(session, asset_id: int):
        query = select(AssetPrice).where(AssetPrice.asset_id == asset_id)
        result = await session.execute(query)
        asserts = result.scalars().all()
        return asserts
    
    