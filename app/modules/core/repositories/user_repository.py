from sqlmodel import Session
from app.common.base_repository import BaseRepository
from app.modules.core.models.user import User

class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, User)
