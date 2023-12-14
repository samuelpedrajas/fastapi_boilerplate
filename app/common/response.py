from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from typing import Optional


T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    status: int
    message: str
    result: Optional[T] = None


def standard_response(status: int, message: str, result: Optional[T] = None) -> StandardResponse[T]:
    return StandardResponse[T](status=status, message=message, result=result)
