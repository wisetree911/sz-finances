from __future__ import annotations

from collections.abc import AsyncIterator

import app.models  # noqa: F401
import pytest
from app.core.config import settings
from app.infrastructure.db.database import Base, get_session
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

test_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_session() -> AsyncIterator[object]:
    async with test_session_maker() as session:
        yield session


def _ensure_test_database() -> None:
    database_name = test_engine.url.database or ''
    if 'test' not in database_name:
        raise RuntimeError(
            'API tests require DATABASE_URL pointing to a dedicated test database '
            "(database name must contain 'test')."
        )


async def _truncate_all_tables() -> None:
    table_names = [table.name for table in reversed(Base.metadata.sorted_tables)]
    if not table_names:
        return

    joined = ', '.join(f'"{table_name}"' for table_name in table_names)
    async with test_engine.begin() as conn:
        await conn.execute(text(f'TRUNCATE TABLE {joined} RESTART IDENTITY CASCADE'))


@pytest.fixture(scope='session', autouse=True)
async def prepare_database() -> AsyncIterator[None]:
    _ensure_test_database()
    app.dependency_overrides[get_session] = override_get_session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    app.dependency_overrides.pop(get_session, None)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncIterator[None]:
    await _truncate_all_tables()
    yield
    await _truncate_all_tables()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as async_client:
        yield async_client
