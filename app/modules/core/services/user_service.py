from typing import List
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.common.base_service import BaseService
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserCreate, UserUpdate, UserResponse, UserFilters
from app.modules.core.integrity_validators.user_integrity_validator import UserIntegrityValidator
from app.modules.core.repositories.user_repository import UserRepository
from app.modules.core.services.role_service import RoleService, get_role_service
from app.modules.core.services.country_service import CountryService, get_country_service
from app.modules.core.services.file_service import FileService, get_file_service
from app.common.security import get_password_hash
from app.common.db import get_db
from config import settings


class UserService(BaseService):
    def __init__(
        self, request: Request, repository: UserRepository, role_service: RoleService,
        country_service: CountryService, file_service: FileService,
        user_integrity_validator: UserIntegrityValidator
    ):
        self.request = request
        self.repository = repository
        self.role_service = role_service
        self.country_service = country_service
        self.file_service = file_service
        self.user_integrity_validator = user_integrity_validator

    async def create_user(self, user_data: UserCreate, active: bool = False) -> User:
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

    async def get_user_response_from_user(self, user: User) -> UserResponse:
        await self.repository.ensure_relationships_loaded(user, ["country"])
        user_data = user.__dict__.copy()
        user_data["country"] = await self.country_service.get_country_response_from_country(user.country)
        if user.photo_path:
            user_data["photo_url"] = self.file_service.get_url(user.photo_path)
        return UserResponse.model_validate(user_data)

    async def get_filtered(self, user_filters: UserFilters, page: int, per_page: int) -> List[UserResponse]:
        query = user_filters.apply_filters()
        users = await self.repository.paginate(query, page, per_page)
        users['items'] = [await self.get_user_response_from_user(user) for user in users['items']]
        return users

    async def delete_user(self, user: User) -> bool:
        if user.photo_path:
            try:
                await self.file_service.delete_file(user.photo_path)
            except:
                pass
        await self.repository.delete(user)
        await self.repository.commit()
        return True


def get_user_service(request: Request, db: AsyncSession = Depends(get_db)) -> UserService:
    user_repository = UserRepository(db)
    role_service = get_role_service(db)
    country_service = get_country_service(db)
    return UserService(
        request,
        user_repository,
        role_service,
        country_service,
        get_file_service(request),
        UserIntegrityValidator(user_repository, role_service, country_service)
    )
