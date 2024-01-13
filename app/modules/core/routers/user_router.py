from fastapi import APIRouter, Depends, Query, UploadFile, Form, File
from fastapi.exceptions import ValidationException
from app.modules.core.models.user import User
from app.modules.core.schemas.user_schemas import UserCreate, UserResponse, UserUpdate, UserFilters
from app.modules.core.services.user_service import UserService, get_user_service
from app.modules.core.services.auth_service import has_permission
from app.common.response import standard_response, StandardResponse
from app.common.paginator import PaginatedResponse


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
    user_response = await user_service.get_user_response_from_user(user)
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
    current_user: User = Depends(has_permission("admin")),
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
    except ValidationException as e:
        return standard_response(422, "Validation error", e.errors())

    validation_errors = await user_service.validate_data_update(user_data)

    if validation_errors:
        return standard_response(422, "Validation error", validation_errors)

    user = await user_service.get_first_by_field('id', user_id)
    user = await user_service.update_user(user, user_data)
    user_response = await user_service.get_user_response_from_user(user)
    return standard_response(200, None, user_response)


@router.post(
    "/admin/users",
    response_model=StandardResponse[UserResponse],
    tags=["Users"]
)
async def post_user(
    username: str = Form(...),
    password: str = Form(...),
    password_confirmation: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    country_id: int = Form(...),
    photo: UploadFile = File(None),
    role_id: str = Form(None),
    current_user: User = Depends(has_permission("admin")),
    user_service: UserService = Depends(get_user_service)
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
                photo=photo,
                role_id=role_id
            )
        except Exception as e:
            return standard_response(422, "Validation error", e.errors())

        validation_errors = await user_service.validate_data_create(user_data)

        if validation_errors:
            return standard_response(422, "Validation error", validation_errors)

        user = await user_service.create_user(user_data, True)
        user_response = await user_service.get_user_response_from_user(user)
        return standard_response(200, None, user_response)


@router.get(
    '/admin/users',
    response_model=PaginatedResponse[UserResponse],
    tags=["Users"]
)
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=0),
    user_filters: UserFilters = Depends(),
    current_user: User = Depends(has_permission("admin")),
    user_service: UserService = Depends(get_user_service)
):
    paginated_results = await user_service.get_filtered(user_filters, page, per_page)
    return standard_response(200, None, paginated_results)
