import logging
from fastapi import APIRouter, Depends, Request, UploadFile, Form, File
from fastapi.templating import Jinja2Templates
from app.modules.core.models.user import User
from app.modules.core.schemas.auth_schemas import Token, LoginForm
from app.modules.core.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.modules.core.services.user_service import UserService, get_user_service
from app.modules.core.services.auth_service import has_permission
from app.common.response import standard_response, StandardResponse
from app.schemas import ValidationErrorSchema
from typing import List, Union

router = APIRouter()

@router.get(
    "/admin/users/{user_id}",
    response_model=StandardResponse[UserResponse],
    tags=["Users"]
)
async def get_user(
    user_id: int,
    current_user: User = Depends(has_permission("admin")),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_first_by_field('id', user_id)
    user_response = user_service.get_user_response_from_user(user)
    return standard_response(200, None, user_response)


@router.put(
    "/admin/users/{user_id}",
    response_model=StandardResponse[UserResponse],
    tags=["Users"]
)
async def put_user(
    user_id: int,
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    country_id: int = Form(...),
    photo: UploadFile = File(None),
    user_service: UserService = Depends(get_user_service)
):

    user_data = None
    try:
        user_data = UserUpdate(
            name=name,
            surname=surname,
            email=email,
            country_id=country_id,
            photo=photo
        )
    except Exception as e:
        return standard_response(422, "Validation error", e.errors())

    validation_errors = await user_service.validate_data_update(user_data)

    if validation_errors:
        return standard_response(422, "Validation error", validation_errors)

    user = await user_service.get_first_by_field('id', user_id)
    user = await user_service.update_user(user, user_data)
    user_response = user_service.get_user_response_from_user(user)
    return standard_response(200, None, user_response)
