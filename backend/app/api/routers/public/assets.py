from app.api.dependencies import get_asset_service
from app.schemas.asset import AssetResponse
from app.schemas.common.pagination import Page
from app.services.assets import AssetService
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix='/assets', tags=['Assets'])


@router.get(
    '/{asset_id}',
    response_model=AssetResponse,
    summary='Информация об активе.',
)
async def get_asset_by_id(
    asset_id: int, service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    return await service.get_by_id(asset_id=asset_id)


@router.get(
    '/by-ticker/{ticker}',
    response_model=AssetResponse,
    summary='Информация об активе по тикеру.',
)
async def get_asset_by_ticker(
    ticker: str, service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    return await service.get_by_ticker(ticker=ticker)


@router.get(
    '/',
    response_model=Page[AssetResponse],
    summary='Все активы рынка.',
)
async def get_assets(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: AssetService = Depends(get_asset_service),
) -> Page[AssetResponse]:
    items, total = await service.get_all(limit=limit, offset=offset)
    return Page[AssetResponse](items=items, total=total, limit=limit, offset=offset)
