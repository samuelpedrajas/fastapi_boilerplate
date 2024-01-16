from app.common.base_repository import BaseRepository
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.modules.core.models.user import Permission

class PermissionRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Permission)
