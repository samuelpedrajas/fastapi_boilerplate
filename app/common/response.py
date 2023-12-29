from typing import Generic, TypeVar, Optional, Dict
from pydantic import BaseModel
from fastapi.responses import JSONResponse


T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    status: int
    message: Optional[str] = None
    result: Optional[T] = None


def standard_response(
    status: int,
    message: str,
    result: Optional[T] = None,
    headers: Optional[Dict[str, str]] = None
) -> StandardResponse[T]:
    content = StandardResponse[T](status=status, message=message, result=result).model_dump()
    return JSONResponse(content=content, status_code=status, headers=headers)