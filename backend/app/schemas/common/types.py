from decimal import Decimal
from typing import Annotated

from pydantic import Field

Money = Annotated[
    Decimal,
    Field(description='Money value.', ge=0),
]

Percent = Annotated[
    Decimal,
    Field(description='Percent value.', ge=-100),
]

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

PortfolioName = Annotated[
    str,
    Field(
        description='Portfolio name',
        min_length=1,
        max_length=64,
        examples=['Main portfolio'],
    ),
]
