from fastapi import Depends
from sqlmodel import Session
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserCreate
from app.modules.core.services.user_service import UserService, get_user_service
from app.common.db import get_db


class AuthService:
    def __init__(self, db: Session, user_service: UserService):
        self.db = db
        self.user_service = user_service

    def register(self, user_data: UserCreate) -> User:
        user = self.user_service.create_user(user_data, "user", False)

        # Send confirmation email
        email_template = db.query(EmailTemplate).filter_by(name='account_confirmation').first()
        if email_template:
            email_content = email_template.render(user)
            send_email(user.email, email_template.subject, email_content)

        return user


def get_auth_service(db: Session = Depends(get_db)) -> UserService:
    return AuthService(db, get_user_service(db))
