from fastapi import APIRouter, status
from app.schemas.portfolio import PortfolioCreate, PortfolioResponse
from app.core.database import SessionDep
from app.services.portfolios import PortfolioService
router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.get("/", response_model=list[PortfolioResponse])
async def get_all(session: SessionDep):
    return await PortfolioService.get_all_portfolios(session=session)

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_by_id(session: SessionDep, portfolio_id: int):
    return await PortfolioService.get_portfolio_by_portfolio_id(session=session, portfolio_id=portfolio_id)

@router.post("/{portfolio_id}", response_model=PortfolioResponse)
async def create(session: SessionDep, portfolio_schema: PortfolioCreate):
    return await PortfolioService.create_portfolio(session=session, portfolio_schema=portfolio_schema)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(session: SessionDep, portfolio_id: int):
    await PortfolioService.delete_portfolio_by_portfolio_id(session=session, portfolio_id=portfolio_id)
    return

@router.get("/user/{user_id}")
async def get_user_portfolios(session: SessionDep, user_id: int):
    return await PortfolioService.get_user_portfolios(session=session, user_id=user_id)

