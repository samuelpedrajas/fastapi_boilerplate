import aiofiles
from typing import Any, List
from datetime import datetime, timedelta
from fastapi import Depends, Request
from sqlalchemy import Select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.common.base_service import BaseService
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserFilters
from app.modules.core.repositories.user_repository import UserRepository
from app.modules.core.services.role_service import RoleService, get_role_service
from app.modules.core.services.country_service import CountryService, get_country_service
from app.modules.core.services.file_service import FileService, get_file_service
from app.common.security import get_password_hash
from app.common.db import get_db
from app.schemas import ValidationErrorSchema
from config import settings


class UserAlreadyExistsException(Exception):
    message = "User already exists"


class UserService(BaseService):
    def __init__(self, request: Request, repository: UserRepository, role_service: RoleService, country_service: CountryService, file_service: FileService):
        self.request = request
        self.repository = repository
        self.role_service = role_service
        self.country_service = country_service
        self.file_service = file_service

    async def create_user(self, user_data: UserCreate, active: bool = False) -> User:
        if await self.user_already_exists(user_data, clean_up_non_active=True):
            raise UserAlreadyExistsException()

        photo_path = None
        transaction = None
        try:
            if user_data.photo:
                photo_path = await self.file_service.save_file(user_data.photo, settings.UPLOADS_DIR)

            transaction = await self.repository.db.begin_nested()
            new_user = User(
                username=user_data.username,
                password_hash=get_password_hash(user_data.password),
                name=user_data.name,
                surname=user_data.surname,
                email=user_data.email,
                country_id=user_data.country_id,
                photo_path=photo_path,
                active=active
            )

            new_user = await self.repository.create(new_user)
            await self.repository.flush()

            # add roles
            await self.repository.ensure_relationships_loaded(new_user, ["roles"])
            if user_data.role_ids:
                for role_id in user_data.role_ids:
                    role = await self.role_service.get_first_by_field('id', role_id)
                    new_user.roles.append(role)
            else:
                # Assign default role
                role = await self.role_service.get_first_by_field('name', 'user')
                new_user.roles.append(role)

            await self.repository.commit()
            return await self.repository.refresh(new_user)
        except Exception as e:
            if transaction is not None:
                await transaction.rollback()
            try:
                if photo_path is not None:
                    await self.file_service.delete_file(photo_path)
            except:
                pass
            raise e

    async def update_user_password(self, user: User, password: str) -> User:
        user.password_hash = get_password_hash(password)
        await self.repository.commit()

    async def update_user(self, user: User, user_data: UserUpdate) -> User:
        user.name = user_data.name
        user.surname = user_data.surname
        user.country_id = user_data.country_id

        if user.photo_path:
            try:
                await self.file_service.delete_file(user.photo_path)
            except:
                pass

        if user_data.photo:
            user.photo_path = await self.file_service.save_file(user_data.photo, settings.UPLOADS_DIR)
        else:
            user.photo_path = None

        await self.repository.commit()
        return await self.repository.refresh(user)

    async def activate_user(self, user: User) -> User:
        if not user.active:
            user.active = True
            await self.repository.commit()
            return True
        return False

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
            user = user[0]
            if user.active:
                return True

            if user.created_at > account_creation_limit:
                return True

        # only clean up if users are not active and timeout has passed
        if clean_up_non_active:
            for user in users:
                await self.repository.delete(user)

        return False        

    async def get_user_response_from_user(self, user: User) -> UserResponse:
        await self.repository.ensure_relationships_loaded(user, ["country"])
        user_data = user.__dict__.copy()
        user_data["country"] = await self.country_service.get_country_response_from_country(user.country)
        if user.photo_path:
            user_data["photo_url"] = self.file_service.get_url(user.photo_path)
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

        return validation_errors

    async def validate_data_create(self, user_data: UserCreate) -> List[ValidationErrorSchema]:
        validation_errors = await self.validate_data_base(user_data)

        if await self.user_data_already_exists("email", user_data.email):
            validation_errors.append(
                ValidationErrorSchema(
                    loc=("body", "email",),
                    msg="Email already exists",
                    type="db_error.duplicate",
                )
            )

        if await self.user_data_already_exists("username", user_data.username):
            validation_errors.append(
                ValidationErrorSchema(
                    loc=("body", "username",),
                    msg="Username already exists",
                    type="db_error.duplicate",
                )
            )

        for role_id in user_data.role_ids:
            if await self.role_service.get_first_by_field('id', role_id) is None:
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


    async def get_filtered(self, user_filters: UserFilters, page: int, per_page: int) -> List[UserResponse]:
        query = user_filters.apply_filters()
        users = await self.repository.paginate(query, page, per_page)
        users['items'] = [await self.get_user_response_from_user(user) for user in users['items']]
        return users


def get_user_service(request: Request, db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(
        request,
        UserRepository(db),
        get_role_service(db),
        get_country_service(db),
        get_file_service(request)
    )
