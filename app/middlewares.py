from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from contextvars import ContextVar
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware import Middleware


request_object: ContextVar[Request] = ContextVar('request')


class RequestToContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_object.set(request)
        response = await call_next(request)
        return response


middlewares = [Middleware(RequestToContextMiddleware)]