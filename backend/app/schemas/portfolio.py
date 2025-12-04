from pydantic import BaseModel
from datetime import datetime

class PortfolioBase(BaseModel):
    user_id: int
    name: str
    currency: str
    
class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(PortfolioBase):
    user_id: int | None = None
    name: str | None = None

class PortfolioResponse(PortfolioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

