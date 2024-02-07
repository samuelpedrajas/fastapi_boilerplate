from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.common.base_service import BaseService
from app.modules.core.repositories.role_repository import RoleRepository
from app.common.db import get_db
from app.modules.core.models.user import Role
from app.modules.core.schemas.user_schemas import RoleResponse


class RoleService(BaseService):
    async def get_role_response_from_role(self, role: Role) -> RoleResponse:
        role_data = role.__dict__.copy()
        return RoleResponse.model_validate(role_data)


def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(RoleRepository(db))
