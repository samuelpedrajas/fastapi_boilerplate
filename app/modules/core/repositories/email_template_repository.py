from sqlmodel.ext.asyncio.session import AsyncSession
from app.common.base_repository import BaseRepository
from app.modules.core.models.email_template import EmailTemplate

class EmailTemplateRepository(BaseRepository[EmailTemplate]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, EmailTemplate)
