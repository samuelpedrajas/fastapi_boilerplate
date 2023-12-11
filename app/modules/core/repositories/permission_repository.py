from app.common.base_repository import BaseRepository
from sqlmodel import Session
from app.modules.core.models.user import Permission

class PermissionRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Permission)
