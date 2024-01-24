from pydantic import BaseModel, Field
from typing import Generic, List, Dict, Any, Optional, TypeVar


T = TypeVar('T')


class ValidationErrorSchema(BaseModel):
    loc: List[str] = Field(...)
    msg: str = Field(...)
    type: str = Field(...)
    ctx: Dict[str, Any] = Field(None)


class StandardResponse(BaseModel, Generic[T]):
    status: int
    message: Optional[str] = None
    result: Optional[T] = None
