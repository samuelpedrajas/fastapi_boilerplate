from pydantic import BaseModel, field_validator, constr

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
    password: constr(min_length=8, max_length=50)
    password_confirmation: constr(min_length=8, max_length=50)

    _password_confirmation = field_validator('password_confirmation')(check_passwords_match)
