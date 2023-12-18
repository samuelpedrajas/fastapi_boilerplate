from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.core.repositories.country_repository import CountryRepository
from app.common.db import get_db


class CountryService:

    def __init__(self, db: AsyncSession, repository: CountryRepository):
        self.db = db
        self.repository = repository

    async def get_country_by_id(self, id: int):
        return await self.repository.get_by_id(id)


def get_country_service(db: AsyncSession = Depends(get_db)) -> CountryService:
    return CountryService(db, CountryRepository(db))
