from pydantic import BaseModel, field_validator

from app.modules.core.schemas.schema_validators import check_passwords_match


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginForm(BaseModel):
    username: str
    password: str


class RequestPasswordResetForm(BaseModel):
    email: str


class ResetPasswordForm(BaseModel):
    token: str
    password: str
    password_confirmation: str

    _password_confirmation = field_validator('password_confirmation')(check_passwords_match)
