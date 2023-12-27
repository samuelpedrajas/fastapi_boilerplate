import aiofiles
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserCreate
from app.modules.core.repositories.user_repository import UserRepository
from app.modules.core.schemas.user_schemas import UserResponse
from app.modules.core.services.role_service import RoleService, get_role_service
from app.helpers.encryption import hash_password
from app.common.db import get_db
from app.helpers.uploads import save_file
from config import settings


class UserService:
    def __init__(self, repository: UserRepository, role_service: RoleService):
        self.repository = repository
        self.role_service = role_service

    async def create_user(self, user_data: UserCreate, role_name: str = "user", active: bool = False) -> User:
        user = await self.user_service.get_user_by_username(user_data.username)
        if user and user.active:
            raise Exception("User already exists")
        if user:
            await self.user_service.delete_user(user)

        filepath = None
        try:
            if user_data.photo:
                filepath = await save_file(user_data.photo, settings.UPLOADS_DIR)

            transaction = self.repository.db.begin_nested()
            new_user = User(
                username=user_data.username,
                password_hash=hash_password(user_data.password),
                name=user_data.name,
                surname=user_data.surname,
                email=user_data.email,
                country_id=user_data.country_id,
                photo_path=filepath,
                active=active
            )

            # Assign default role
            role = await self.role_service.get_role_by_name(role_name)
            new_user.roles.append(role)

            return await self.repository.create(new_user)
        except SQLAlchemyError as e:
            transaction.rollback()
            try:
                if filepath is not None:
                    await aiofiles.os.remove(filepath)
            except:
                pass
            raise e

    async def update_user(self, user: User) -> User:
        return await self.repository.update(user)

    async def delete_user(self, user: User) -> None:
        await self.repository.delete(user)

    async def get_user_by_id(self, id: int) -> User:
        return await self.repository.get_by_id(id)

    async def get_user_by_username(self, username: str) -> User:
        return await self.repository.get_by_username(username)

    def get_user_response_from_user(self, user: User) -> UserResponse:
        # Note: Slight coupling between service and repository
        user_data = user.model_dump()
        user_data["country"] = user.country.model_dump()
        return UserResponse.model_validate(user_data)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db), get_role_service(db))
