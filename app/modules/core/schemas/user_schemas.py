from typing import Optional
from datetime import datetime, timedelta
from pydantic import EmailStr, constr, validator
from pydantic_core import PydanticCustomError
from fastapi import UploadFile, File
from app.helpers.uploads import validate_file_size
from app.modules.core.schemas.country_schemas import CountryResponse
from app.schemas import ValidationErrorSchema, BaseModel
from config import settings


class UserCreate(BaseModel):

    photo: Optional[UploadFile] = File(None)
    username: constr(min_length=2, max_length=50)
    password: constr(min_length=8, max_length=50)
    password_confirmation: constr(min_length=8, max_length=50)
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    email: EmailStr
    country_id: int

    @validator('photo')
    def validate_photo(cls, v):
        if v and v.content_type not in ["image/jpeg", "image/png"]:
            raise PydanticCustomError(
                'invalid_photo_format',
                'Invalid photo format. Only JPEG or PNG images are allowed.',
            )
        return v

    @validator('photo')
    def validate_photo_size(cls, v):
        max_size = 1024 * 1024 * 20  # 20MB
        if v and not validate_file_size(v.file, max_size):
            raise PydanticCustomError(
                'photo_too_large',
                'Photo must be less than {max_size} bytes.',
            )
        return v

    async def validate_data(self, user_service, country_service):
        validation_errors = []
        timeout_duration = timedelta(seconds=settings.ACCOUNT_ACTIVATION_TIMEOUT)
        account_creation_limit = datetime.utcnow() - timeout_duration
        user = await user_service.get_user_by_username(self.username)
        if user and (user.active or user.created_at > account_creation_limit):
            validation_errors.append(
                ValidationErrorSchema(
                    loc=("body", "username",),
                    msg="Username already exists",
                    type="db_error.duplicate",
                )
            )
        if await country_service.get_country_by_id(self.country_id) is None:
            validation_errors.append(
                ValidationErrorSchema(
                    loc=("body", "country_id",),
                    msg="Invalid country",
                    type="db_error.not_found",
                )
            )
        return validation_errors


class UserResponse(BaseModel):

    username: constr(min_length=2, max_length=50)
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    email: EmailStr
    country: Optional[CountryResponse] = None
