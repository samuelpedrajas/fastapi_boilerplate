import os, logging
from typing import List
from logging.handlers import RotatingFileHandler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi import FastAPI
from app.modules.core.routers.auth_router import router as auth_router, web_router as web_auth_router
from app.modules.core.routers.user_router import router as user_router
from app.modules.core.routers.file_router import router as file_router
from app.modules.core.routers.params_router import router as params_router
from app.modules.core.routers.root_router import router as root_router
from app.error_handlers import validation_exception_handler, http_exception_handler, starlette_http_exception_handler
from app.schemas import ValidationErrorSchema
from app.common.response import StandardResponse
from app.middlewares import middlewares
from config import settings


def create_app():
    # create app
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
        middleware=middlewares
    )

    # include routers
    app.include_router(root_router, prefix='')
    app.include_router(auth_router, prefix='/api/v1')
    app.include_router(web_auth_router, prefix='/web')
    app.include_router(user_router, prefix='/api/v1')
    app.include_router(params_router, prefix='/api/v1')
    app.include_router(file_router)

    # configure logging
    log_file = os.getenv('LOG_FILE', settings.LOG_FILE)
    log_level = os.getenv('LOG_LEVEL', logging.INFO)
    file_handler = RotatingFileHandler(log_file, maxBytes=104857600, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(log_level)
    logging.getLogger().addHandler(file_handler)

    return app
