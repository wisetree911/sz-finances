from typing import Annotated

from app.infrastructure.db.database import get_session
from app.repositories import (
    AssetRepositoryPostgres,
    PortfolioRepositoryPostgres,
    TradeRepositoryPostgres,
    UserRepositoryPostgres,
)
from app.repositories.analytics import AnalyticsRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_portfolio_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PortfolioRepositoryPostgres:
    return PortfolioRepositoryPostgres(session=session)


async def get_trade_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TradeRepositoryPostgres:
    return TradeRepositoryPostgres(session=session)


async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepositoryPostgres:
    return UserRepositoryPostgres(session=session)


async def get_asset_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AssetRepositoryPostgres:
    return AssetRepositoryPostgres(session=session)


async def get_analytics_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AnalyticsRepository:
    return AnalyticsRepository(session=session)
