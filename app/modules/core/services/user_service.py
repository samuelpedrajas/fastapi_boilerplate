from fastapi import Depends
from passlib.context import CryptContext
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserCreate
from app.modules.core.repositories.user_repository import UserRepository
from app.modules.core.schemas.user_schemas import UserResponse
from app.modules.core.services.role_service import RoleService, get_role_service
from app.common.db import get_db


class UserService:
    def __init__(self, db: Session, repository: UserRepository, role_service: RoleService):
        self.db = db
        self.repository = repository
        self.role_service = role_service

    def create_user(self, user_data: UserCreate, role_name: str = "user", active: bool = False) -> User:
        try:
            transaction = db.begin_nested()
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            new_user = User(
                username=user_data.username,
                password_hash=pwd_context.hash(user_data.password),
                name=user_data.name,
                surname=user_data.surname,
                email=user_data.email,
                country_id=user_data.country_id,
                photo_path=user_data.filepath,
                active=active
            )

            # Assign default role
            role = self.role_service.get_role_by_name(role_name)
            if role:
                new_user.roles.append(role)

            return self.repository.create(new_user)
        except SQLAlchemyError as e:
            transaction.rollback()
            raise e

    def get_user_response_from_user(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db, UserRepository(db), get_role_service(db))
