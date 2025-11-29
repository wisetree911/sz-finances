from fastapi import APIRouter, status, Depends
from app.schemas.portfolio import PortfolioCreate, PortfolioResponse
from app.services.portfolios import PortfolioService
from app.api.deps import get_porfolio_session
router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_by_id(portfolio_id: int, service: PortfolioService=Depends(get_porfolio_session)):
    return await service.get_portfolio_by_portfolio_id(portfolio_id=portfolio_id)

@router.get("/", response_model=list[PortfolioResponse])
async def get_all(service: PortfolioService=Depends(get_porfolio_session)):
    return await service.get_all_portfolios()

@router.post("/{portfolio_id}", response_model=PortfolioResponse)
async def create(portfolio_schema: PortfolioCreate, service: PortfolioService = Depends(get_porfolio_session)):
    return await service.create_portfolio(portfolio_schema=portfolio_schema)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(portfolio_id: int, service: PortfolioService=Depends(get_porfolio_session)):
    await service.delete_portfolio_by_portfolio_id(portfolio_id=portfolio_id)
    return

@router.get("/user/{user_id}")
async def get_user_portfolios(user_id: int, service: PortfolioService=Depends(get_porfolio_session)):
    return await service.get_user_portfolios(user_id=user_id)

