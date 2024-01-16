from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.common.base_service import BaseService
from app.modules.core.repositories.country_repository import CountryRepository
from app.common.db import get_db


class CountryService(BaseService):
    pass


def get_country_service(db: AsyncSession = Depends(get_db)) -> CountryService:
    return CountryService(CountryRepository(db))
