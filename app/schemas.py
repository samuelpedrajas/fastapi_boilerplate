from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any


class ValidationErrorSchema(BaseModel):
    loc: List[str] = Field(...)
    msg: str = Field(...)
    type: str = Field(...)
    ctx: Dict[str, Any] = Field(None)
