from app.common.base_repository import BaseRepository
from sqlmodel import Session
from app.modules.core.models.role import Role

class RoleRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Role)

    def get_role_by_name(self, name: str) -> Role:
        return self.db.exec(self.model).filter(self.model.name == name).first()
