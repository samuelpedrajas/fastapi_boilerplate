import os
import shutil
from werkzeug.utils import secure_filename
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
from fastapi import Request, Response
from fastapi.templating import Jinja2Templates
from app.modules.core.models import User, Role
from app.modules.core.schema import RegistrationForm
from app.helpers.email_service import send_email
from app.modules.core.models import EmailTemplate
from app.helpers.encryption import Encryption
from app.dependencies.db import get_db  # Assuming you have a dependency to get the DB session

router = APIRouter()

@router.post("/register/")
async def register(
    form_data: RegistrationForm,
    # photo: UploadFile | None = None,
    db: Session = Depends(get_db)
):
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

    try:
        # Start DB transaction
        transaction = db.begin_nested()

        # Create user instance
        new_user = User(
            username=form_data.username,
            password_hash=generate_password_hash(form_data.password),
            name=form_data.name,
            surname=form_data.surname,
            email=form_data.email,
            country_id=form_data.country_id,
            photo_path=filepath,
            active=False
        )

        # Assign default role
        default_role = db.query(Role).filter_by(role_name='user').first()
        if default_role:
            new_user.roles.append(default_role)

        db.add(new_user)
        db.commit()

        # Send confirmation email
        email_template = db.query(EmailTemplate).filter_by(name='account_confirmation').first()
        if email_template:
            email_content = email_template.render(new_user)
            send_email(new_user.email, email_template.subject, email_content)

        return {"status": 200, "message": "Registration successful", "user_id": new_user.id}

    except SQLAlchemyError as e:
        transaction.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Assuming you have a Jinja2Templates instance set up for rendering HTML templates
templates = Jinja2Templates(directory="app/modules/core/templates")

@router.get("/confirm/")
async def confirm(token: str, request: Request, db: Session = Depends(get_db)):
    if not token:
        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "No token provided."}, status_code=400)

    try:
        encryption = Encryption("your-secret-key")  # Replace with actual secret key or config
        user_id = int(encryption.decrypt(token))
        user = db.query(User).get(user_id)

        if not user or user.active:
            return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "Invalid or expired token."}, status_code=400)

        user.active = True
        db.commit()

        return templates.TemplateResponse("confirmation_success.html", {"request": request})
        
    except Exception as e:
        # Replace with your logging mechanism
        print(e)  # Example: replace with actual logging
        return templates.TemplateResponse("confirmation_error.html", {"request": request, "message": "An error occurred during confirmation."}, status_code=500)