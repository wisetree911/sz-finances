from typing import Annotated, Generic, TypeVar

from app.schemas.common.enums import AssetSector, AssetType
from pydantic import BaseModel, ConfigDict, Field, PositiveInt

T = TypeVar('T')


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)


AssetTypeField = Annotated[AssetType, Field(description='Вид актива')]

AssetSectorField = Annotated[AssetSector, Field(description='Сектор, к которому относится акция')]

Ticker = Annotated[
    str,
    Field(
        min_length=1,
        max_length=12,
        pattern=r'^[A-Z0-9._-]+$',
        description='Тикер, уникальный индентификатор актива на бриже',
        examples=['SBER', 'GAZP', 'T'],
    ),
]

AssetFullName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=200,
        description='Полное название актива',
        examples=['Газпром', 'Сбербанк ПАО'],
    ),
]


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')


class AssetFields(APIModel):
    ticker: Ticker
    full_name: AssetFullName
    type: AssetTypeField
    sector: AssetSectorField


class AssetResponse(AssetFields):
    id: PositiveInt


class AssetCreate(AssetFields):
    pass


class AssetUpdate(AssetFields):
    ticker: Ticker | None = None
    full_name: AssetFullName | None = None
    type: AssetTypeField | None = None
    sector: AssetSectorField | None = None
