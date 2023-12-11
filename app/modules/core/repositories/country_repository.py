from app.common.base_repository import BaseRepository
from sqlmodel import Session
from app.modules.core.models.user import Country

class CountryRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Country)

    def get_country_by_code(self, code: str) -> Country:
        return self.db.exec(self.model).filter(self.model.code == code).first()
