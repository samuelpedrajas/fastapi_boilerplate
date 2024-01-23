from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.common.base_service import BaseService
from app.modules.core.repositories.country_repository import CountryRepository
from app.common.db import get_db
from app.modules.core.models.user import Country
from app.modules.core.schemas.country_schemas import CountryResponse


class CountryService(BaseService):
    async def get_country_response_from_country(self, country: Country) -> CountryResponse:
        country_data = country.__dict__.copy()
        return CountryResponse.model_validate(country_data)


def get_country_service(db: AsyncSession = Depends(get_db)) -> CountryService:
    return CountryService(CountryRepository(db))
