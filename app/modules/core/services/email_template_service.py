from fastapi import Depends
from sqlmodel import Session
from app.modules.core.models.email_template import EmailTemplate
from app.modules.core.repositories.email_template_repository import EmailTemplateRepository
from app.common.db import get_db
from app.modules.core.models.user import User
from app.modules.core.models.email_template import EmailTemplate
from app.helpers.encryption import encrypt


class EmailTemplateService:
    def __init__(self, db: Session, repository: EmailTemplateRepository):
        self.db = db
        self.repository = repository

    @staticmethod
    def generate_confirmation_url(user):
        token = encrypt(str(user.id))
        # Generate the URL dynamically
        confirmation_url = url_for('auth.confirmation', token=token, _external=True)
        return confirmation_url

    def get_email_template_by_name(self, name: str) -> EmailTemplate:
        return self.repository.get_email_template_by_name(name)

    def render(self, user: User, email_template: EmailTemplate) -> str:
        # Mapping known variables
        variables = {
            '@@name@@': user.name,
            '@@surname@@': user.surname,
            '@@username@@': user.username,
            '@@confirmation_url@@': self.generate_confirmation_url(user)
        }

        # Replacing variables in the template
        rendered_body = self.html_body
        for var, value in variables.items():
            if value is not None:
                rendered_body = rendered_body.replace(var, value)
            else:
                rendered_body = rendered_body.replace(var, '')

        return rendered_body


def get_email_template_service(db: Session = Depends(get_db)) -> EmailTemplateService:
    return EmailTemplateService(db, EmailTemplateRepository(db))
