from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.common.base_service import BaseService
from app.modules.core.models.email_template import EmailTemplate
from app.modules.core.repositories.email_template_repository import EmailTemplateRepository
from app.common.db import get_db
from app.modules.core.models.email_template import EmailTemplate


class EmailTemplateService(BaseService):
    def render(self, context: dict, email_template: EmailTemplate) -> str:     
        rendered_body = email_template.html_body
        for var in email_template.email_variables:  # Note: Slight coupling between service and repository
            value = context[var.variable]  # raise error on missing key
            rendered_body = rendered_body.replace(f'@@{var.variable}@@', str(value))
        
        return rendered_body

def get_email_template_service(db: AsyncSession = Depends(get_db)) -> EmailTemplateService:
    return EmailTemplateService(EmailTemplateRepository(db))
