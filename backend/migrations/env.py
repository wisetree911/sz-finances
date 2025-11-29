from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

from app.core.database import Base
from app.core.config import settings

from shared.models.user import User
from shared.models.asset import Asset
from shared.models.asset_price import AssetPrice
from shared.models.portfolio import Portfolio
from shared.models.portfolio_position import PortfolioPosition
from shared.models.trade import Trade


config = context.config

# Подтягиваем конфиг логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Пробрасываем строку подключения
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# метаданные всех таблиц
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в офлайн-режиме"""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполняем миграции в обычном режиме"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Async миграции"""
    connectable = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())