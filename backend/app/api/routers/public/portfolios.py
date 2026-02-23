from app.api.dependencies import get_portfolio_service
from app.core.security.dependencies import get_current_user
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
)
from app.services.portfolios import PortfolioService
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix='/portfolios', tags=['Portfolios'])


@router.get(
    '/',
    response_model=list[PortfolioResponse],
    summary='Список всех портфелей пользователя.',
)  # todo
async def get_portfolios(
    current_user=Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> list[PortfolioResponse]:
    return await service.get_user_portfolios(user_id=current_user.id)


@router.get(
    '/{portfolio_id}',
    response_model=PortfolioResponse,
    summary='Портфель по id.',
)
async def get_by_portfolio_id(
    portfolio_id: int,
    current_user=Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioResponse:
    return await service.get_portfolio_for_user(portfolio_id=portfolio_id, user_id=current_user.id)


@router.delete(
    '/{portfolio_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить портфель по id.',
)
async def delete_by_id(
    portfolio_id: int,
    current_user=Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    await service.delete_portfolio_for_user(portfolio_id=portfolio_id, user_id=current_user.id)
    return None


@router.post(
    '/',
    response_model=PortfolioResponse,
    summary='Создать пустой портфель.',
)  # todo
async def create_portfolio_for_user(
    payload: PortfolioCreate,
    current_user=Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioResponse:
    return await service.create_portfolio_for_user(payload=payload, user_id=current_user.id)


@router.patch(
    '/{portfolio_id}',
    response_model=PortfolioResponse,
    summary='Обновить информацию о портфеле.',
)
async def update_portfolio_for_user(
    portfolio_id: int,
    payload: PortfolioUpdate,
    current_user=Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioResponse:
    return await service.update_for_user(
        portfolio_id=portfolio_id, user_id=current_user.id, payload=payload
    )
