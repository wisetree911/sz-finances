# TODO: make endpoints ко всем хуйням описанным в айпаде (юри норм сделать тоже по ресту)
from fastapi import Depends, status
from fastapi import APIRouter
from app.core.database import SessionDep
from app.services.assets import AssetService
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.api.deps import get_asset_service
router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset_by_id(asset_id: int, service: AssetService=Depends(get_asset_service)):
    return await service.get_by_id(asset_id=asset_id)

@router.get("/by-ticker/{ticker}", response_model=AssetResponse)
async def get_asset_by_ticker(ticker: str, service: AssetService=Depends(get_asset_service)):
    return await service.get_by_ticker(ticker=ticker)

@router.get("/", response_model=list[AssetResponse])
async def get_assets(service: AssetService=Depends(get_asset_service)):
    return await service.get_all()

@router.post("/", response_model=AssetResponse)
async def create_asset(asset_schema: AssetCreate, service: AssetService=Depends(get_asset_service)):
    return await service.create(asset_schema=asset_schema)

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: int, service: AssetService=Depends(get_asset_service)):
    await service.delete(asset_id=asset_id)
    return

@router.patch("/{asset_id}")
async def update_asset(asset_id: int, payload: AssetUpdate, service: AssetService=Depends(get_asset_service)):
    updated = await service.update(asset_id=asset_id, data=payload.dict(exclude_unset=True))
    return updated
## TODO : add sector column to other cruds