from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from fastapi import Form, UploadFile, File
from .country_schemas import CountryResponse


class UserCreate(BaseModel):

    photo: UploadFile = File(None)
    username: constr(min_length=2, max_length=50) = Form()
    password: constr(min_length=8, max_length=50) = Form()
    password_confirmation: constr(min_length=8, max_length=50) = Form()
    name: constr(min_length=2, max_length=50) = Form()
    surname: constr(min_length=2, max_length=50) = Form()
    email: EmailStr = Form()
    country_id: int = Form()


class UserResponse(BaseModel):

    username: constr(min_length=2, max_length=50)
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    email: EmailStr
    country: Optional[CountryResponse] = None
