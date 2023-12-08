from fastapi import Depends
from sqlmodel import Session
from app.modules.core.models.email_template import EmailTemplate
from app.modules.core.repositories.email_template_repository import EmailTemplateRepository
from app.common.db import get_db
from app.modules.core.models.email_template import EmailTemplate


class EmailTemplateService:
    def __init__(self, db: Session, repository: EmailTemplateRepository):
        self.db = db
        self.repository = repository

    def get_email_template_by_name(self, name: str) -> EmailTemplate:
        return self.repository.get_email_template_by_name(name)


def get_email_template_service(db: Session = Depends(get_db)) -> EmailTemplateService:
    return EmailTemplateService(db, EmailTemplateRepository(db))
