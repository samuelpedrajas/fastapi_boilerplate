import logging
from typing import List, Union
from fastapi import APIRouter, Depends, Request, UploadFile, Form, File
from fastapi.exceptions import ValidationException
from fastapi.templating import Jinja2Templates
from app.modules.core.models.user import User
from app.modules.core.schemas.auth_schemas import Token, LoginForm, RequestPasswordResetForm, ResetPasswordForm
from app.modules.core.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.modules.core.services.user_service import UserService, get_user_service
from app.modules.core.services.auth_service import AuthService, get_auth_service, has_permission
from app.common.response import standard_response, StandardResponse
from app.schemas import ValidationErrorSchema
from app.common.rate_limiting import rate_limit


router = APIRouter()


# Note: there's no native way to use Pydantic models with Form data
@router.post(
    "/auth/register",
    response_model=Union[StandardResponse[UserResponse], StandardResponse[List[ValidationErrorSchema]]],
    name="auth.register",
    tags=["Auth"]
)
@rate_limit(max_requests=6, window=60)
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

    user_service = auth_service.user_service
    validation_errors = await user_service.user_integrity_validator.validate_data_create(user_data)

    if validation_errors:
        return standard_response(422, "Validation error", validation_errors)

    try:
        user = await auth_service.register(user_data)
        user_response = await auth_service.user_service.get_user_response_from_user(user)
        return standard_response(200, "Registration successful", user_response)
    except Exception as e:
        raise e


@router.post(
    "/auth/login",
    response_model=StandardResponse[Token],
    tags=["Auth"]
)
@rate_limit(max_requests=6, window=60)
async def login(
    request: Request,
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
    request: Request,
    current_user: User = Depends(has_permission("base")),
    user_service: UserService = Depends(get_user_service)
):
    response_user = await user_service.get_user_response_from_user(current_user)
    return standard_response(200, None, response_user)


@router.put(
    "/auth/me",
    response_model=StandardResponse[UserResponse],
    tags=["Auth"]
)
async def put_user(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    country_id: int = Form(...),
    photo: UploadFile = File(None),
    current_user: User = Depends(has_permission("base")),
    user_service: UserService = Depends(get_user_service)
):
    user_data = None
    try:
        user_data = UserUpdate(
            name=name,
            surname=surname,
            country_id=country_id,
            photo=photo
        )
    except ValidationException as e:
        return standard_response(422, "Validation error", e.errors())

    validation_errors = await user_service.user_integrity_validator.validate_data_update(user_data)

    if validation_errors:
        return standard_response(422, "Validation error", validation_errors)

    current_user = await user_service.update_user(current_user, user_data)
    user_response = await user_service.get_user_response_from_user(current_user)
    return standard_response(200, None, user_response)


@router.post(
    "/auth/request_password_reset",
    response_model=StandardResponse,
    tags=["Auth"]
)
async def request_password_reset(
    request: Request,
    form_data: RequestPasswordResetForm,
    auth_service: AuthService = Depends(get_auth_service)
):
    success = await auth_service.send_password_reset_email(form_data.email)
    if not success:
        return standard_response(404, "User not found", None)

    return standard_response(
        200,
        "An e-mail has been sent to your e-mail address with instructions "
        "on how to reset your password.",
        None
    )


@router.post(
    "/auth/reset_password",
    response_model=StandardResponse,
    name="auth.reset_password",
    tags=["Auth"]
)
async def reset_password(
    reset_password_form: ResetPasswordForm,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.get_user_from_token(reset_password_form.token)
    if not user:
        return standard_response(404, "User not found", None)

    try:
        await auth_service.user_service.update_user_password(user, reset_password_form.password)
        return standard_response(200, "Password reset successful", None)
    except Exception as e:
        raise e


## Web routes
web_router = APIRouter()


templates = Jinja2Templates(directory="app/modules/core/templates")


@web_router.get(
    "/auth/confirm/",
    include_in_schema=False,
    name="auth.confirm",
    tags=["Auth"]
)
async def confirm(
    request: Request,
    token: str,
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


@web_router.get(
    "/auth/reset_password",
    name="auth.reset_password_form",
    include_in_schema=False,
    tags=["Auth"]
)
async def reset_password(
    token: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    if not token:
        return templates.TemplateResponse("reset_password.html", {"request": request, "message": "No token provided."}, status_code=400)

    try:
        user = await auth_service.get_user_from_token(token)
        if not user:
            return templates.TemplateResponse("reset_password.html", {"request": request, "message": "The token is invalid."}, status_code=400)

        reset_password_url = str(request.url_for("auth.reset_password"))
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "reset_password_url": reset_password_url,
                "token": token
            },
            status_code=400
        )

    except Exception as e:
        logging.error(e)
        return templates.TemplateResponse("reset_password.html", {"request": request, "message": "An error occurred while resetting your password."}, status_code=500)
