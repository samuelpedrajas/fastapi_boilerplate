from app.common.base_repository import BaseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.core.models.user import Country

class CountryRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Country)

    async def get_country_by_code(self, code: str) -> Country:
        results = await self.db.exec(self.model).filter(self.model.code == code)
        return results.first()
