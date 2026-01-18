from app.api.deps import get_current_user, get_trade_service
from app.schemas.trade import TradeResponse
from app.services.trades import TradeService
from fastapi import APIRouter, Depends

router = APIRouter(prefix='/trades', tags=['Trades'])


@router.get('/{trade_id}', response_model=TradeResponse)
async def get_trade_for_user(
    trade_id: int,
    current_user=Depends(get_current_user),
    service: TradeService = Depends(get_trade_service),
) -> TradeResponse:
    return await service.get_trade_by_id_for_user(trade_id=trade_id, user_id=current_user.id)


@router.get('/portfolio/{portfolio_id}', response_model=list[TradeResponse])
async def get_portfolio_trades_for_user(
    portfolio_id: int,
    current_user=Depends(get_current_user),
    service: TradeService = Depends(get_trade_service),
) -> list[TradeResponse]:
    return await service.get_trades_portfolio_for_user(
        portfolio_id=portfolio_id, user_id=current_user.id
    )
