from fastapi import APIRouter, status
from app.schemas.portfolio_position import PortfolioPositionCreate
from app.core.database import SessionDep
from app.services.portfolio_positions import PortfolioPositionService

router = APIRouter(prefix="/portfolio_positions", tags=["Portfolio Positions"])


@router.get("/{portfolio_position}")
async def get_portfolio_position(session: SessionDep, portfolio_position_id: int):
    return await PortfolioPositionService.get_by_id(
        session=session,
        portfolio_position_id=portfolio_position_id
    )

@router.get("/")
async def get_portfolio_positions(session: SessionDep):
    return await PortfolioPositionService.get_all(session=session)

@router.post("/")
async def create_portfolio_position(session: SessionDep, portfolio_position_schema: PortfolioPositionCreate):
    return await PortfolioPositionService.create(
        session=session,
        portfolio_position_schema=portfolio_position_schema
    )

@router.delete("/{portfolio_position}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(session: SessionDep, portfolio_position_id: int):
    await PortfolioPositionService.delete(
        session=session,
        portfolio_position_id=portfolio_position_id
    )
    return 
