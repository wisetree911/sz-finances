from fastapi import APIRouter, status
from app.schemas.trade import TradeCreate, TradeResponse
from app.core.database import SessionDep
from app.services.trades import TradeService

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(session: SessionDep, trade_id: int):
    return await TradeService.get_trade_by_trade_id(session=session, trade_id=trade_id)

@router.get("/", response_model=list[TradeResponse])
async def get_trades(session: SessionDep):
    return await TradeService.get_all_trades(session=session)

@router.post("/", response_model=TradeResponse)
async def create_trade(session: SessionDep, trade_schema: TradeCreate):
    return await TradeService.create_trade(session=session, trade_schema=trade_schema)

@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(session: SessionDep, trade_id: int):
    await TradeService.delete_trade(session=session, trade_id=trade_id)
    return
    