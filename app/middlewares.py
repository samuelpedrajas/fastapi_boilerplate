from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from contextvars import ContextVar
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from config import settings


request_object: ContextVar[Request] = ContextVar('request')


class RequestToContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_object.set(request)
        response = await call_next(request)
        return response


cors_origins = settings.CORS_ORIGINS.split(',')


middlewares = [
    Middleware(RequestToContextMiddleware),
    Middleware(CORSMiddleware, allow_origins=cors_origins, allow_methods=["*"], allow_headers=["*"])
]
