from app.common.base_repository import BaseRepository
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.core.models.user import Role

class RoleRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Role)

    async def get_role_by_name(self, name: str) -> Role:
        statement = select(self.model).where(self.model.name == name)
        results = await self.db.exec(statement)
        return results.first()
