from fastapi import Depends
from sqlmodel import Session
from app.modules.core.models.role import Role
from app.modules.core.repositories.role_repository import RoleRepository
from app.common.db import get_db
from app.modules.core.models.role import Role


class RoleService:
    def __init__(self, db: Session, repository: RoleRepository):
        self.db = db
        self.repository = repository

    def get_role_by_name(self, name: str) -> Role:
        return self.repository.get_role_by_name(name)


def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db, RoleRepository(db))
