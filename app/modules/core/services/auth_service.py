from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserCreate
from app.modules.core.services.user_service import UserService, get_user_service
from app.modules.core.services.email_template_service import EmailTemplateService, get_email_template_service
from app.modules.core.services.email_service import EmailService, get_email_service
from app.common.db import get_db
from app.helpers.security import encrypt, decrypt, verify_password
from config import settings


bearer_scheme = HTTPBearer(auto_error=False)

class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(401, "Unauthorized")


class AuthService:
    ALGORITHM = "HS256"

    def __init__(self, user_service: UserService, email_template_service: EmailTemplateService, email_service: EmailService):
        self.user_service = user_service
        self.email_template_service = email_template_service
        self.email_service = email_service

    async def register(self, user_data: UserCreate, confirmation_url: str) -> User:
        user = await self.user_service.create_user(user_data, False)

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
        if not user:
            return False
        return await self.user_service.activate_user(user)

    async def authenticate_user(self, username: str, password: str):
        user = await self.user_service.get_first_by_field('username', username, relationships_to_load=['roles', 'roles.permissions'])
        if not user or not verify_password(password, user.password_hash) or not user.active:
            return None
        return user

    @classmethod
    def create_access_token(cls, user: User) -> str:
        token_life = settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS
        expire = datetime.utcnow() + timedelta(days=token_life)
        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "surname": user.surname,
            "role": [{"id": role.id, "name": role.name} for role in user.roles],
            "active": user.active,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: int = int(payload.get("sub"))
            if user_id is None:
                raise UnauthorizedException()
        except JWTError:
            raise UnauthorizedException()
        user = await self.user_service.get_first_by_field('id', user_id, relationships_to_load=['roles', 'roles.permissions'])
        if user is None:
            raise UnauthorizedException()
        return user


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(get_user_service(db), get_email_template_service(db),
                       get_email_service()) 


async def get_current_user(bearer_token = Depends(bearer_scheme), auth_service: AuthService = Depends(get_auth_service)):
    if not bearer_token or not bearer_token.credentials:
        raise UnauthorizedException()
    token = bearer_token.credentials
    return await auth_service.get_current_user(token)


def has_permission(required_permission: str):
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = {perm.name for role in current_user.roles for perm in role.permissions}
        if not required_permission in user_permissions:
            raise UnauthorizedException()
        return current_user
    return permission_checker
