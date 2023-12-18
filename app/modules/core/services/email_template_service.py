from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.core.models.email_template import EmailTemplate
from app.modules.core.repositories.email_template_repository import EmailTemplateRepository
from app.common.db import get_db
from app.modules.core.models.email_template import EmailTemplate


class EmailTemplateService:
    def __init__(self, db: AsyncSession, repository: EmailTemplateRepository):
        self.db = db
        self.repository = repository

    async def get_email_template_by_name(self, name: str) -> EmailTemplate:
        return await self.repository.get_email_template_by_name(name)

    def render(self, context: dict, email_template: EmailTemplate) -> str:
        # Fetch required variables for this template from the database
        
        rendered_body = email_template.html_body
        for var in email_template.email_variables:  # Note: Slight coupling between service and repository
            value = context[var.variable]  # raise error on missing key
            rendered_body = rendered_body.replace(f'@@{var.variable}@@', str(value))
        
        return rendered_body

def get_email_template_service(db: AsyncSession = Depends(get_db)) -> EmailTemplateService:
    return EmailTemplateService(db, EmailTemplateRepository(db))
