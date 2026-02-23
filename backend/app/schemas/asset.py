from typing import Generic, TypeVar
from app.schemas.common.types import Ticker, AssetFullName
from app.schemas.common.enums import AssetSector, AssetType
from pydantic import BaseModel, ConfigDict, Field, PositiveInt

T = TypeVar('T')


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')


class AssetFields(APIModel):
    ticker: Ticker
    full_name: AssetFullName
    type: AssetType
    sector: AssetSector


class AssetResponse(AssetFields):
    id: PositiveInt


class AssetCreate(AssetFields):
    pass


class AssetUpdate(AssetFields):
    ticker: Ticker | None = None
    full_name: AssetFullName | None = None
    type: AssetType | None = None
    sector: AssetSector | None = None
