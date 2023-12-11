from sqlmodel import Session, select
from app.common.base_repository import BaseRepository
from app.modules.core.models.email_template import EmailTemplate

class EmailTemplateRepository(BaseRepository[EmailTemplate]):
    def __init__(self, db: Session):
        super().__init__(db, EmailTemplate)

    def get_email_template_by_name(self, name: str) -> EmailTemplate:
        statement = select(EmailTemplate).where(EmailTemplate.name == name)
        results = self.db.exec(statement)
        return results.first()
