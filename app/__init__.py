import os, logging
from typing import List
from logging.handlers import RotatingFileHandler
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI
from dotenv import load_dotenv
from app.modules.core.routers.auth_router import router as auth_router
from app.error_handlers import validation_exception_handler
from app.schemas import ValidationError
from app.common.response import StandardResponse
from config import settings

def configure_logging():
    log_file = os.getenv('LOG_FILE', settings.LOG_FILE)
    log_level = os.getenv('LOG_LEVEL', logging.INFO)
    file_handler = RotatingFileHandler(log_file, maxBytes=104857600, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(log_level)
    logging.getLogger().addHandler(file_handler)

def create_app():
    load_dotenv()
    app = FastAPI(
        exception_handlers={RequestValidationError: validation_exception_handler},
        responses={
            422: {
                "description": "Validation Error",
                "model": StandardResponse[List[ValidationError]],
            },
        },
    )

    configure_logging()

    app.include_router(auth_router, prefix='/v1/auth')

    return app
