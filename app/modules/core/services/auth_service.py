from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserCreate
from app.modules.core.services.user_service import UserService, get_user_service
from app.modules.core.services.email_template_service import EmailTemplateService, get_email_template_service
from app.modules.core.services.email_service import EmailService, get_email_service
from app.common.db import get_db
from app.helpers.encryption import encrypt, decrypt


class AuthService:
    def __init__(self, user_service: UserService, email_template_service: EmailTemplateService, email_service: EmailService):
        self.user_service = user_service
        self.email_template_service = email_template_service
        self.email_service = email_service

    async def register(self, user_data: UserCreate, confirmation_url: str) -> User:
        user = await self.user_service.create_user(user_data, "user", False)

        # Send confirmation email
        email_template = await self.email_template_service.get_first_by_field("name", "account_confirmation")
        if email_template:
            context = {
                "name": user.name,
                "surname": user.surname,
                "confirmation_url": confirmation_url + "?token=" + encrypt(user.id)
            }
            email_content = self.email_template_service.render(context, email_template)
            await self.email_service.send_email(user.email, email_template.subject, email_content)

        return user

    async def confirm(self, token: str) -> bool:
        user_id = int(decrypt(token))
        user = await self.user_service.get_first_by_field('id', user_id)
        if user and not user.active:
            user.active = True
            user = await self.user_service.update(user)
            return True
        return False

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(get_user_service(db), get_email_template_service(db),
                       get_email_service()) 
