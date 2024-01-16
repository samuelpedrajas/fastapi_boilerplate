from app.common.base_repository import BaseRepository
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.modules.core.models.user import Role

class RoleRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Role)
