from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.core.repositories.role_repository import RoleRepository
from app.common.db import get_db
from app.modules.core.models.user import Role


class RoleService:
    def __init__(self, db: AsyncSession, repository: RoleRepository):
        self.db = db
        self.repository = repository

    async def get_role_by_name(self, name: str) -> Role:
        return await self.repository.get_role_by_name(name)


def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(db, RoleRepository(db))
