import logging
from fastapi import APIRouter, Depends, Request, UploadFile, Form, File
from sqlalchemy.exc import SQLAlchemyError
from fastapi.templating import Jinja2Templates
from app.modules.core.schemas.user_schemas import UserCreate, UserResponse
from app.modules.core.services.auth_service import AuthService, get_auth_service
from app.modules.core.services.country_service import CountryService, get_country_service
from app.common.response import standard_response, StandardResponse
from app.schemas import ValidationErrorSchema
from typing import List, Union

router = APIRouter()

# Note: there's no native way to use Pydantic models with Form data
@router.post("/register/", response_model=Union[StandardResponse[UserResponse], StandardResponse[List[ValidationErrorSchema]]], name="auth.register")
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
    auth_service: AuthService = Depends(get_auth_service),
    country_service: CountryService = Depends(get_country_service)
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
    except Exception as e:
        return standard_response(422, "Validation error", e.errors())

    validation_errors = await user_data.validate_data(country_service)

    if validation_errors:
        return standard_response(422, "Validation error", validation_errors)
        
    try:
        confirmation_url = str(request.url_for("auth.confirm"))
        user = await auth_service.register(user_data, confirmation_url)
        user_response = auth_service.user_service.get_user_response_from_user(user)
        return standard_response(200, "Registration successful", user_response)
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
    


# Assuming you have a Jinja2Templates instance set up for rendering HTML templates
templates = Jinja2Templates(directory="app/modules/core/templates")

@router.get("/confirm/", include_in_schema=False, name="auth.confirm")
async def confirm(
    token: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    if not token:
        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "No token provided."}, status_code=400)

    try:
        user = await auth_service.confirm(token)

        if user and not user.active:
            return templates.TemplateResponse("confirmation_success.html", {"request": request})

        if user and user.active:
            return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "Account already confirmed."}, status_code=400)

        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "Invalid token."}, status_code=400)
        
    except Exception as e:
        logging.error(e)
        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "An error occurred during confirmation."}, status_code=500)