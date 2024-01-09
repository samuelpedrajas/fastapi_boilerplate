import os, logging
from typing import List
from logging.handlers import RotatingFileHandler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi import FastAPI
from dotenv import load_dotenv
from app.modules.core.routers.auth_router import router as auth_router
from app.modules.core.routers.user_router import router as user_router
from app.error_handlers import validation_exception_handler, http_exception_handler, starlette_http_exception_handler
from app.schemas import ValidationErrorSchema
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
        exception_handlers={
            RequestValidationError: validation_exception_handler,
            HTTPException: http_exception_handler,
            StarletteHTTPException: starlette_http_exception_handler,  # Add this line
        },
        responses={
            422: {
                "description": "Validation Error",
                "model": StandardResponse[List[ValidationErrorSchema]],
            },
        },
    )

    app.include_router(auth_router, prefix='/v1')
    app.include_router(user_router, prefix='/v1')

    configure_logging()

    return app
