from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from config import settings

engine = create_async_engine(settings.sqlalchemy_database_url)
metadata = SQLModel.metadata
sqlalchemy_database_url = settings.sqlalchemy_database_url

async def get_db():
    async with AsyncSession(engine) as session:
        yield session
