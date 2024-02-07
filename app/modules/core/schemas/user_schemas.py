from typing import Dict, List, Optional, Tuple
from pydantic import EmailStr, constr, field_validator, BaseModel as BaseSchema
from fastapi import UploadFile, File
from app.modules.core.schemas.country_schemas import CountryResponse
from app.common.filtering import BaseFiltering, FilterConfig, enhanced_ilike, equals
from app.modules.core.models.user import User
from app.modules.core.schemas.schema_validators import check_passwords_match, validate_photo, validate_photo_size


class UserBase(BaseSchema):
    photo: Optional[UploadFile] = File(None)
    role_ids: List[int]

    _validate_photo = field_validator('photo')(validate_photo)

    _validate_photo_size = field_validator('photo')(validate_photo_size)


class UserCreate(UserBase):
    username: constr(min_length=2, max_length=50)
    password: constr(min_length=8, max_length=50)
    password_confirmation: constr(min_length=8, max_length=50)
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    email: EmailStr
    country_id: int

    _password_confirmation = field_validator('password_confirmation')(check_passwords_match)


class UserUpdate(UserBase):
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    country_id: int
    role_ids: List[int]


class RoleResponse(BaseSchema):
    id: int
    name: constr(min_length=2, max_length=50)


class UserResponse(BaseSchema):
    id: int
    username: constr(min_length=2, max_length=50)
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    email: EmailStr
    country: Optional[CountryResponse] = None
    roles: List[RoleResponse]
    photo_url: Optional[str] = None


class UserFilters(BaseFiltering):
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    country_id: Optional[int] = None
    country__name: Optional[str] = None
    roles__id: Optional[int] = None
    roles__name: Optional[str] = None

    def filters_config(self) ->  Tuple[User, Dict[str, FilterConfig]]:
        return User, {
            'full_name': FilterConfig(
                model_fields=['name', 'surname'],
                comparison=enhanced_ilike,
            ),
            'email': FilterConfig(
                model_fields=['email'],
                comparison=enhanced_ilike,
            ),
            'username': FilterConfig(
                model_fields=['username'],
                comparison=enhanced_ilike,
            ),
            'country_id': FilterConfig(
                model_fields=['country_id'],
                comparison=equals,
            ),
            'country__name': FilterConfig(
                model_fields=['country.name'],
                comparison=enhanced_ilike,
            ),
            'roles__id': FilterConfig(
                model_fields=['roles.id'],
                comparison=equals,
            ),
            'roles__name': FilterConfig(
                model_fields=['roles.name'],
                comparison=enhanced_ilike,
            )
        }
