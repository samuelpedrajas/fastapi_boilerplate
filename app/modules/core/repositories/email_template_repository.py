from sqlmodel import Session
from app.common.base_repository import BaseRepository
from app.modules.core.models.email_template import EmailTemplate


class EmailTemplateRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, EmailTemplate)

    def get_by_name(self, name: str) -> EmailTemplate:
        return self.db.exec(EmailTemplate).filter(EmailTemplate.name == name).first()
