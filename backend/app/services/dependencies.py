from typing import Annotated

from app.infrastructure.db.database import get_session
from app.repositories import (
    AssetRepositoryPostgres,
    PortfolioRepositoryPostgres,
    TradeRepositoryPostgres,
    UserRepositoryPostgres,
)
from app.repositories.analytics import AnalyticsRepository
from app.repositories.dependencies import (
    get_analytics_repo,
    get_asset_repo,
    get_portfolio_repo,
    get_trade_repo,
    get_user_repo,
)
from app.services.analytics import AnalyticsService
from app.services.assets import AssetService
from app.services.auth import AuthService
from app.services.portfolios import PortfolioService
from app.services.trades import TradeService
from app.services.users import UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_portfolio_service(
    repo: Annotated[PortfolioRepositoryPostgres, Depends(get_portfolio_repo)],
) -> PortfolioService:
    return PortfolioService(repo=repo)


async def get_trade_service(
    repo: Annotated[TradeRepositoryPostgres, Depends(get_trade_repo)],
) -> TradeService:
    return TradeService(repo=repo)


async def get_user_service(
    repo: Annotated[UserRepositoryPostgres, Depends(get_user_repo)],
) -> UserService:
    return UserService(repo=repo)


async def get_asset_service(
    repo: Annotated[AssetRepositoryPostgres, Depends(get_asset_repo)],
) -> AssetService:
    return AssetService(repo=repo)


async def get_auth_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AuthService:
    return AuthService(session=session)


async def get_analytics_service(repo: Annotated[AnalyticsRepository, Depends(get_analytics_repo)]):
    return AnalyticsService(repo=repo)
