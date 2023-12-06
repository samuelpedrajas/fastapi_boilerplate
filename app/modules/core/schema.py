from pydantic import BaseModel, EmailStr, constr, validator
from sqlalchemy.future import select
from app.dependencies.db import get_db
from app.modules.core.models import User, Country
from fastapi import Form

class RegistrationForm(BaseModel):
    username: constr(min_length=2, max_length=50) = Form()
    password: constr(min_length=8, max_length=50) = Form()
    password_confirmation: constr(min_length=8, max_length=50) = Form()
    name: constr(min_length=2, max_length=50) = Form()
    surname: constr(min_length=2, max_length=50) = Form()
    email: EmailStr = Form()
    country_id: int = Form()

    @validator('password_confirmation')
    def validate_password_confirmation(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Password confirmation does not match.')
        return v

    # Username and email validators would be asynchronous
    @validator('username')
    async def validate_username(cls, v, values, **kwargs):
        async with get_db() as session:
            result = await session.execute(select(User).filter(User.username == v, User.deleted_at == None))
            user = result.scalars().first()
            if user:
                raise ValueError('Username already in use.')
        return v

    @validator('email')
    async def validate_email(cls, v, values, **kwargs):
        async with get_db() as session:
            result = await session.execute(select(User).filter(User.email == v, User.deleted_at == None))
            user = result.scalars().first()
            if user:
                raise ValueError('Email already in use.')
        return v

    @validator('country_id')
    async def validate_country_id(cls, v):
        async with get_db() as session:
            country = await session.get(Country, v)
            if not country:
                raise ValueError('Invalid country.')
        return v
