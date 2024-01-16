from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.common.base_service import BaseService
from app.modules.core.repositories.role_repository import RoleRepository
from app.common.db import get_db


class RoleService(BaseService):
    pass


def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(RoleRepository(db))
