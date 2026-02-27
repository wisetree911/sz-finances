from app.contracts.repos import PortfolioRepository, TradeRepository, UserRepository
from app.infrastructure.db.database import get_session
from app.repositories import (
    AssetRepositoryPostgres,
    PortfolioRepositoryPostgres,
    TradeRepositoryPostgres,
    UserRepositoryPostgres,
)
from app.repositories.analytics import AnalyticsRepository
from app.services.analytics import AnalyticsService
from app.services.assets import AssetService
from app.services.auth import AuthService
from app.services.portfolios import PortfolioService
from app.services.trades import TradeService
from app.services.users import UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_portfolio_repo(session: AsyncSession = Depends(get_session)) -> PortfolioRepository:
    return PortfolioRepositoryPostgres(session=session)


async def get_portfolio_service(
    repo: PortfolioRepository = Depends(get_portfolio_repo),
) -> PortfolioService:
    return PortfolioService(repo=repo)


async def get_trade_repo(session: AsyncSession = Depends(get_session)) -> TradeRepository:
    return TradeRepositoryPostgres(session=session)


async def get_trade_service(repo: TradeRepository = Depends(get_trade_repo)) -> TradeService:
    return TradeService(repo=repo)


async def get_user_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepositoryPostgres(session=session)


async def get_user_service(repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(repo=repo)


async def get_asset_repo(session: AsyncSession = Depends(get_session)) -> AssetRepositoryPostgres:
    return AssetRepositoryPostgres(session=session)


async def get_asset_service(
    repo: AssetRepositoryPostgres = Depends(get_asset_repo),
) -> AssetService:
    return AssetService(repo=repo)


async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session=session)


async def get_analytics_repo(session: AsyncSession = Depends(get_session)) -> AnalyticsRepository:
    return AnalyticsRepository(session=session)


async def get_analytics_service(repo: AnalyticsRepository = Depends(get_analytics_repo)):
    return AnalyticsService(repo=repo)
