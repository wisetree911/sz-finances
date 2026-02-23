from app.api.dependencies import get_portfolio_service
from app.core.security.dependencies import require_admin
from app.schemas.portfolio import (
    PortfolioCreateAdm,
    PortfolioListResponse,
    PortfolioResponse,
    PortfolioUpdate,
)
from app.services.portfolios import PortfolioService
from fastapi import APIRouter, Depends, status

router = APIRouter(
    prefix='/portfolios',
    tags=['Portfolios'],
    dependencies=[Depends(require_admin)],
)


@router.get('/{portfolio_id}')
async def get_by_id(
    portfolio_id: int, service: PortfolioService = Depends(get_portfolio_service)
) -> PortfolioResponse:
    return await service.get_portfolio_by_portfolio_id(portfolio_id=portfolio_id)


@router.get('/', response_model=PortfolioListResponse)
async def get_all(
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioListResponse:
    res = await service.get_all_portfolios()
    return PortfolioListResponse(portfolios=res)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=PortfolioResponse)
async def create(  # обработку если нет юзера
    payload: PortfolioCreateAdm,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioResponse:
    return await service.create_portfolio(payload)


@router.delete('/{portfolio_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(
    portfolio_id: int, service: PortfolioService = Depends(get_portfolio_service)
):
    await service.delete_portfolio_by_portfolio_id(portfolio_id=portfolio_id)
    return


@router.patch('/{portfolio_id}')
async def update_portfolio(
    portfolio_id: int,
    payload: PortfolioUpdate,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioResponse:
    return await service.update(portfolio_id=portfolio_id, payload=payload)


@router.get('/user/{user_id}', response_model=PortfolioListResponse)  # add pydantic
async def get_user_portfolios(
    user_id: int, service: PortfolioService = Depends(get_portfolio_service)
):
    res = await service.get_user_portfolios(user_id=user_id)
    return PortfolioListResponse(portfolios=res)
