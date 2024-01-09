from typing import Optional
from pydantic import EmailStr, constr, field_validator, validator
from pydantic_core import PydanticCustomError
from fastapi import UploadFile, File
from app.helpers.uploads import validate_file_size
from app.modules.core.schemas.country_schemas import CountryResponse
from app.schemas import BaseModel
from config import settings


class UserBase(BaseModel):

    photo: Optional[UploadFile] = File(None)

    @field_validator('photo')
    def validate_photo(cls, v):
        if v and v.content_type not in ["image/jpeg", "image/png"]:
            raise PydanticCustomError(
                'invalid_photo_format',
                'Invalid photo format. Only JPEG or PNG images are allowed.',
            )
        return v

    @field_validator('photo')
    def validate_photo_size(cls, v):
        max_size = 1024 * 1024 * 20  # 20MB
        if v and not validate_file_size(v.file, max_size):
            raise PydanticCustomError(
                'photo_too_large',
                'Photo must be less than {max_size} bytes.',
            )
        return v


class UserCreate(UserBase):
    username: constr(min_length=2, max_length=50)
    password: constr(min_length=8, max_length=50)
    password_confirmation: constr(min_length=8, max_length=50)
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    email: EmailStr
    country_id: int
    role_id: Optional[int] = None

    @validator('password_confirmation')
    def check_passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise PydanticCustomError(
                'password_mismatch',
                'Password and password_confirmation do not match.'
            )
        return v


class UserUpdate(UserBase):
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    email: EmailStr
    country_id: int


class UserResponse(BaseModel):
    id: int
    username: constr(min_length=2, max_length=50)
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    email: EmailStr
    country: Optional[CountryResponse] = None
