from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi import status
from app.common.response import StandardResponse


async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=StandardResponse(
            status=422,
            message="Validation Error",
            result={"detail": exc.errors()}
        ).model_dump()
    )


async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardResponse(
            status=exc.status_code,
            message=exc.detail,
            result=None
        ).model_dump()
    )


async def starlette_http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardResponse(
            status=exc.status_code,
            message=exc.detail,
            result=None
        ).model_dump()
    )
