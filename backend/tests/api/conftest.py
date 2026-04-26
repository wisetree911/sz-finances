from __future__ import annotations

from collections.abc import AsyncIterator

import app.models  # noqa: F401
import pytest
from app.infrastructure.db.database import Base, engine
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text


def _ensure_test_database() -> None:
    database_name = engine.url.database or ''
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
    async with engine.begin() as conn:
        await conn.execute(text(f'TRUNCATE TABLE {joined} RESTART IDENTITY CASCADE'))


@pytest.fixture(scope='session', autouse=True)
async def prepare_database() -> AsyncIterator[None]:
    _ensure_test_database()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


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
