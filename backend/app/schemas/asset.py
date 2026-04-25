from app.schemas.common.enums import AssetSector, AssetType
from app.schemas.common.types import AssetFullName, Ticker
from pydantic import BaseModel, ConfigDict, PositiveInt


class APIModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        from_attributes=True,
    )


class AssetFields(APIModel):
    ticker: Ticker
    full_name: AssetFullName
    type: AssetType
    sector: AssetSector


class AssetResponse(AssetFields):
    id: PositiveInt


class AssetCreate(AssetFields):
    pass


class AssetUpdate(APIModel):
    ticker: Ticker | None = None
    full_name: AssetFullName | None = None
    type: AssetType | None = None
    sector: AssetSector | None = None
