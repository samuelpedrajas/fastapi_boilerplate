from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.templating import Jinja2Templates
from app.modules.core.schemas.user_schemas import UserCreate
from app.modules.core.services.auth_service import AuthService, get_auth_service
from app.helpers.encryption import decrypt
from app.common.response import standard_response


router = APIRouter()

@router.post("/register/")
async def register(
    request: Request,
    user_data: UserCreate,
    # photo: UploadFile | None = None,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        confirmation_url = str(request.url_for("auth.confirm"))
        user = await auth_service.register(user_data, confirmation_url)
        user_response = auth_service.user_service.get_user_response_from_user(user)
        return standard_response(200, "Registration successful", user_response)
    except SQLAlchemyError as e:
        raise e
    
    # Validate form data
    # FastAPI uses Pydantic models for request validation, 
    # so you might not need the same validation check as in Flask

    # Handle file upload
    filepath = None
    # if photo:
    #     filename = secure_filename(photo.filename)  # Ensure you have a secure_filename function
    #     filepath = os.path.join("storage/uploads", filename)
    #     with open(filepath, "wb") as buffer:
    #         shutil.copyfileobj(photo.file, buffer)


# Assuming you have a Jinja2Templates instance set up for rendering HTML templates
templates = Jinja2Templates(directory="app/modules/core/templates")

@router.get("/confirm/", name="auth.confirm")
async def confirm(token: str, request: Request, db: Session = Depends(get_auth_service)):
    if not token:
        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "No token provided."}, status_code=400)

    try:
        # user_id = int(decrypt(token))
        # user = db.query(User).get(user_id)

        # if not user or user.active:
        #     return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "Invalid or expired token."}, status_code=400)

        # user.active = True
        # db.commit()

        return templates.TemplateResponse("confirmation_success.html", {"request": request})
        
    except Exception as e:
        # Replace with your logging mechanism
        print(e)  # Example: replace with actual logging
        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "An error occurred during confirmation."}, status_code=500)