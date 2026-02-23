from app.schemas.common.types import PortfolioName

from app.schemas.common.enums import Currency
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.types import AwareDatetime, PositiveInt


class APIModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        from_attributes=True,
        str_strip_whitespace=True,
    )


class PortfolioFields(APIModel):
    name: PortfolioName
    currency: Currency = Field(..., description='Portfolio currency')


class PortfolioCreate(PortfolioFields):
    pass


class PortfolioCreateAdm(PortfolioCreate):
    user_id: PositiveInt


class PortfolioUpdate(APIModel):
    name: PortfolioName | None = None
    currency: Currency | None = None

    @model_validator(mode='after')
    def at_least_one_field(self):
        if not self.model_dump(exclude_none=True):
            raise ValueError('At least one field must be provided')
        return self


class PortfolioResponse(PortfolioFields):
    id: PositiveInt
    user_id: PositiveInt
    created_at: AwareDatetime


class PortfolioListResponse(APIModel):
    portfolios: list[PortfolioResponse]
