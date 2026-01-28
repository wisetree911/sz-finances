from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import AwareDatetime

T = TypeVar('T')


class AssetFields(BaseModel):
    ticker: str
    full_name: str
    type: str
    sector: str


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)


class AssetResponsePublic(AssetFields):
    id: int
    model_config = ConfigDict(
        from_attributes=True,
    )


class AssetResponseAdm(AssetFields):
    id: int
    created_at: AwareDatetime


class AssetCreateAdm(AssetFields):
    pass


class AssetUpdateAdm(AssetFields):
    ticker: str | None = None
    full_name: str | None = None
    type: str | None = None
    sector: str | None = None
