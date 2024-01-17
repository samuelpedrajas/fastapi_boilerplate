import logging
from fastapi import APIRouter, Depends, Request, UploadFile, Form, File
from fastapi.exceptions import ValidationException
from fastapi.templating import Jinja2Templates
from app.modules.core.models.user import User
from app.modules.core.schemas.auth_schemas import Token, LoginForm
from app.modules.core.schemas.user_schemas import UserCreate, UserResponse
from app.modules.core.services.user_service import UserService, get_user_service
from app.modules.core.services.auth_service import AuthService, get_auth_service, has_permission
from app.common.response import standard_response, StandardResponse
from app.schemas import ValidationErrorSchema
from typing import List, Union

router = APIRouter()

# Note: there's no native way to use Pydantic models with Form data
@router.post(
    "/auth/register",
    response_model=Union[StandardResponse[UserResponse], StandardResponse[List[ValidationErrorSchema]]],
    name="auth.register",
    tags=["Auth"]
)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password_confirmation: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    country_id: int = Form(...),
    photo: UploadFile = File(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    user_data = None
    try:
        user_data = UserCreate(
            username=username,
            password=password,
            password_confirmation=password_confirmation,
            name=name,
            surname=surname,
            email=email,
            country_id=country_id,
            photo=photo
        )
    except ValidationException as e:
        return standard_response(422, "Validation error", e.errors())

    validation_errors = await auth_service.user_service.validate_data_create(user_data)

    if validation_errors:
        return standard_response(422, "Validation error", validation_errors)

    try:
        confirmation_url = str(request.url_for("auth.confirm"))
        user = await auth_service.register(user_data, confirmation_url)
        user_response = await auth_service.user_service.get_user_response_from_user(user)
        return standard_response(200, "Registration successful", user_response)
    except Exception as e:
        raise e


templates = Jinja2Templates(directory="app/modules/core/templates")


@router.get(
    "/auth/confirm/",
    include_in_schema=False,
    name="auth.confirm",
    tags=["Auth"]
)
async def confirm(
    token: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    if not token:
        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "No token provided."}, status_code=400)

    try:
        if await auth_service.confirm(token):
            return templates.TemplateResponse("confirmation_success.html", {"request": request})

        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "The token is invalid or has expired."}, status_code=400)

    except Exception as e:
        logging.error(e)
        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "An error occurred during confirmation."}, status_code=500)


@router.post(
    "/auth/login",
    response_model=StandardResponse[Token],
    tags=["Auth"]
)
async def login(
    form_data: LoginForm,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        return standard_response(401, "Incorrect username or password", None)
    access_token = auth_service.create_access_token(user)
    token = Token(access_token=access_token, token_type="bearer")
    return standard_response(200, "Login successful", token)


@router.get(
    "/auth/me",
    response_model=StandardResponse[UserResponse],
    tags=["Auth"]
)
async def me(
    current_user: User = Depends(has_permission("base")),
    user_service: UserService = Depends(get_user_service)
):
    response_user = await user_service.get_user_response_from_user(current_user)
    return standard_response(200, None, response_user)
