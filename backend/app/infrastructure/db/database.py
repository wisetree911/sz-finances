from app.core.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = settings.DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, echo=False)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with async_session_maker() as session:
        yield session
