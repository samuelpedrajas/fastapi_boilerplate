from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from config import settings, current_env


sqlalchemy_database_url = settings.sqlalchemy_test_database_url if current_env == "testing" else settings.sqlalchemy_database_url
echo = True if current_env == "development" else False
async_engine = create_async_engine(sqlalchemy_database_url, echo=echo)
metadata = SQLModel.metadata


async def get_db():
    async with AsyncSession(async_engine) as session:
        yield session
