from app.common.base_repository import BaseRepository
from sqlmodel import Session, select
from app.modules.core.models.user import Role

class RoleRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Role)

    def get_role_by_name(self, name: str) -> Role:
        statement = select(self.model).where(self.model.name == name)
        results = self.db.exec(statement)
        return results.first()
