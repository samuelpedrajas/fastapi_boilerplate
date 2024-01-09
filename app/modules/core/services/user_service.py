import aiofiles
from typing import Any, List
from datetime import datetime, timedelta
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.common.base_service import BaseService
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserBase, UserCreate, UserUpdate
from app.modules.core.repositories.user_repository import UserRepository
from app.modules.core.schemas.user_schemas import UserResponse
from app.modules.core.services.role_service import RoleService, get_role_service
from app.modules.core.services.country_service import CountryService, get_country_service
from app.helpers.security import get_password_hash
from app.common.db import get_db
from app.helpers.uploads import save_file
from app.schemas import ValidationErrorSchema
from config import settings


class UserAlreadyExistsException(Exception):
    message = "User already exists"


class UserService(BaseService):
    def __init__(self, repository: UserRepository, role_service: RoleService, country_service: CountryService):
        self.repository = repository
        self.role_service = role_service
        self.country_service = country_service

    async def create_user(self, user_data: UserCreate, active: bool = False) -> User:
        if await self.user_already_exists(user_data, clean_up_non_active=True):
            raise UserAlreadyExistsException()

        filepath = None
        try:
            if user_data.photo:
                filepath = await save_file(user_data.photo, settings.UPLOADS_DIR)

            transaction = self.repository.db.begin_nested()
            new_user = User(
                username=user_data.username,
                password_hash=get_password_hash(user_data.password),
                name=user_data.name,
                surname=user_data.surname,
                email=user_data.email,
                country_id=user_data.country_id,
                photo_path=filepath,
                active=active
            )

            if user_data.role_id is not None:
                role = await self.role_service.get_first_by_field('id', user_data.role_id)
                new_user.roles.append(role)
            else:
                # Assign default role
                role = await self.role_service.get_first_by_field('name', 'user')
                new_user.roles.append(role)

            return await self.repository.create(new_user)
        except Exception as e:
            transaction.rollback()
            try:
                if filepath is not None:
                    await aiofiles.os.remove(filepath)
            except:
                pass
            raise e

    async def update_user(self, user: User, user_data: UserUpdate) -> User:
        user.name = user_data.name
        user.surname = user_data.surname
        user.email = user_data.email
        user.country_id = user_data.country_id

        try:
            await aiofiles.os.remove(user.photo_path)
        except:
            pass

        if user_data.photo:
            user.photo_path = await save_file(user_data.photo, settings.UPLOADS_DIR)
        else:
            user.photo_path = None

        return await self.repository.update(user)

    async def user_already_exists(self, user_data: UserCreate, clean_up_non_active: bool = False) -> bool:
        username_exists = await self.user_data_already_exists("username", user_data.username, clean_up_non_active)
        email_exists = await self.user_data_already_exists("email", user_data.email, clean_up_non_active)
        return username_exists or email_exists

    async def user_data_already_exists(self, field: str, value: Any, clean_up_non_active: bool = False) -> bool:
        users = await self.repository.get_by_field(field, value)

        if not users:
            return False

        timeout_duration = timedelta(seconds=settings.ACCOUNT_ACTIVATION_TIMEOUT)
        account_creation_limit = datetime.utcnow() - timeout_duration
        for user in users:
            if user.active:
                return True

            if user.created_at > account_creation_limit:
                return True

        # only clean up if users are not active and timeout has passed
        if clean_up_non_active:
            for user in users:
                await self.repository.delete(user)

        return False        

    def get_user_response_from_user(self, user: User) -> UserResponse:
        # Note: Slight coupling between service and repository
        user_data = user.model_dump()
        user_data["country"] = user.country.model_dump()
        return UserResponse.model_validate(user_data)


    async def validate_data_base(self, user_data: UserBase) -> List[ValidationErrorSchema]:
        validation_errors = []
        if await self.country_service.get_first_by_field('id', user_data.country_id) is None:
            validation_errors.append(
                ValidationErrorSchema(
                    loc=("body", "country_id",),
                    msg="Invalid country",
                    type="db_error.not_found",
                )
            )

        if await self.user_data_already_exists("email", user_data.email):
            validation_errors.append(
                ValidationErrorSchema(
                    loc=("body", "email",),
                    msg="Email already exists",
                    type="db_error.duplicate",
                )
            )

        return validation_errors

    async def validate_data_create(self, user_data: UserCreate) -> List[ValidationErrorSchema]:
        validation_errors = await self.validate_data_base(user_data)

        if await self.user_data_already_exists("username", user_data.username):
            validation_errors.append(
                ValidationErrorSchema(
                    loc=("body", "username",),
                    msg="Username already exists",
                    type="db_error.duplicate",
                )
            )

        if user_data.role_id is not None and await self.role_service.get_first_by_field('id', user_data.role_id) is None:
            validation_errors.append(
                ValidationErrorSchema(
                    loc=("body", "role_id",),
                    msg="Invalid role",
                    type="db_error.not_found",
                )
            )

        return validation_errors

    async def validate_data_update(self, user_data: UserUpdate) -> List[ValidationErrorSchema]:
        validation_errors = await self.validate_data_base(user_data)

        return validation_errors

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db), get_role_service(db), get_country_service(db))
