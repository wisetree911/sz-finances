from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class TopPosition(BaseModel):
    asset_id: int
    ticker: str
    full_name: str
    quantity: int
    avg_buy_price: float
    current_price: float
    current_value: float
    profit: float
    profit_percent: float


class PortfolioShapshotResponse(BaseModel):
    portfolio_id: int
    name: str

    total_value: float
    total_profit: float
    total_profit_percent: float

    invested_value: float

    currency: str

    positions_count: int

    top_positions: List[TopPosition] | None = None