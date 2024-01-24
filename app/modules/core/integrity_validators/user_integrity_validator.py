from datetime import datetime, timedelta
from typing import Any, List
from app.modules.core.repositories.user_repository import UserRepository
from app.modules.core.schemas.user_schemas import UserBase, UserCreate, UserUpdate
from app.schemas import ValidationErrorSchema
from config import settings
from app.modules.core.services.country_service import CountryService
from app.modules.core.services.role_service import RoleService


class UserIntegrityValidator:
    def __init__(self, user_repository: UserRepository, role_service: RoleService, country_service: CountryService):
        self.repository = user_repository
        self.role_service = role_service
        self.country_service = country_service

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

        return validation_errors

    async def validate_data_update(self, user_data: UserUpdate) -> List[ValidationErrorSchema]:
        validation_errors = await self.validate_data_base(user_data)

        return validation_errors
