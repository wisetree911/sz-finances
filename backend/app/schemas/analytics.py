from decimal import Decimal
from enum import Enum
from typing import Annotated

from app.schemas.asset import AssetSector
from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import AwareDatetime, NonNegativeInt, PositiveInt


class APIModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
        json_encoders={Decimal: lambda v: str(v)},
    )


class Currency(str, Enum):
    RUB = 'RUB'
    USD = 'USD'


Money = Annotated[
    Decimal,
    Field(description='Money value.', ge=0),
]

Percent = Annotated[
    Decimal,
    Field(description='Percent value.', ge=-100),
]


class TopPosition(APIModel):
    asset_id: PositiveInt = Field(
        ...,
        description='Asset ID in position',
        examples=[1],
    )
    ticker: str = Field(
        ...,
        description='Asset ticker',
        examples=['GAZP'],
    )
    full_name: str = Field(
        ...,
        description='Full name of asset in position',
        examples=['Газпром'],
    )
    quantity: Decimal = Field(
        ...,
        description='Quantity of asset in position',
        examples=['1.12', '2'],
    )
    avg_buy_price: Money = Field(
        ...,
        description='Average buy price of asset in position',
        examples=['750.54'],
    )
    asset_market_price: Money = Field(
        ...,
        description='Current market price of 1 asset in position.',
        examples=['435.54'],
    )
    market_value: Money = Field(
        ...,
        description='Current market price of all assets in position.',
        examples=['1.12'],
    )
    unrealized_pnl: Decimal = Field(
        ...,
        description='Unrealized PNL of portfolio position.',
        examples=['500.178'],
    )
    unrealized_return_pct: Percent = Field(
        ...,
        description='Profit of asset in percents.',
        examples=['66.0'],
    )
    weight_pct: Percent = Field(
        ...,
        description='Weight of asset in portfolio in percents.',
        examples=['36.12'],
    )


class PortfolioSnapshotResponse(APIModel):
    portfolio_id: PositiveInt = Field(
        ...,
        description='Portfolio ID.',
        examples=[1],
    )
    name: str = Field(..., description='Portfolio name.', examples=['Main portfolio'])
    market_value: Money = Field(
        ...,
        description='Total current value of portfolio',
        examples=['20678.176'],
    )
    unrealized_pnl: Decimal = Field(
        ...,
        description='Unrealized PNL of portfolio',
        examples=['6702.564'],
    )
    unrealized_return_pct: Percent = Field(
        ...,
        description='Unrealized return of portfolio',
        examples=['23.0'],
    )
    cost_basis: Money = Field(
        ...,
        description='Value invested in portfolio initially',
        examples=['16800.12'],
    )
    currency: Currency = Field(
        ...,
        description='Currency of portfolio',
        examples=['RUB', 'USD'],
    )
    positions_count: NonNegativeInt = Field(
        ...,
        description='Number of unique assets in portfolio',
        examples=[14],
    )
    top_positions: list[TopPosition] = Field(
        default_factory=list,
        description='Top 3 positions in portfolio by value part in portfolio.',
        max_length=3,
    )

    @classmethod
    def empty(cls, portfolio):
        return cls(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=Decimal(0),
            unrealized_pnl=Decimal(0),
            unrealized_return_pct=Decimal(0),
            cost_basis=Decimal(0),
            currency=portfolio.currency,
            positions_count=0,
            top_positions=[],
        )


class SectorDistributionPosition(APIModel):
    sector: AssetSector = Field(..., description='Sector name"')
    market_value: Money = Field(
        ...,
        description='Current value of portfolio assets from stated sector.',
        examples=['20678.176'],
    )
    weight_percent: Percent = Field(
        ...,
        description=(
            'Current percent value of portfolio assets from stated sector '
            'to whole current portfolio value.'
        ),
        examples=['23.5'],
    )


class SectorDistributionResponse(APIModel):
    portfolio_id: PositiveInt = Field(
        ...,
        description='Portfolio ID',
        examples=[1],
    )
    name: str = Field(..., description='Portfolio name', examples=['Main portfolio'])
    market_value: Money = Field(
        ...,
        description='Total market value of portfolio',
        examples=['20678.176'],
    )
    currency: Currency = Field(
        ...,
        description='Currency of portfolio',
        examples=['RUB', 'USD'],
    )
    sectors: list[SectorDistributionPosition] = Field(
        default_factory=list,
        description='Portfolio grouped and distributed by sectors',
    )

    @classmethod
    def empty(cls, portfolio):
        return cls(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=Decimal(0),
            currency=portfolio.currency,
            sectors=[],
        )


class PortfolioPrice(APIModel):
    timestamp: AwareDatetime = Field(..., description='Timestamp in iso8601.')
    total_value: Money = Field(..., description='Total value of portfolio at selected timestamp.')


class PortfolioDynamicsResponse(APIModel):
    portfolio_id: PositiveInt = Field(..., description='Portfolio ID.')
    name: str = Field(..., description='Portfolio name.')
    data: list[PortfolioPrice] = Field(
        default_factory=list, description='List of relations timestamp to price.'
    )

    @classmethod
    def empty(cls, portfolio):
        return cls(portfolio_id=portfolio.id, name=portfolio.name, data=[])
