from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ValidationError(BaseModel):
    loc: List[str] = Field(...)
    msg: str = Field(...)
    type: str = Field(...)
    input: str = Field(None)
    ctx: Dict[str, Any] = Field(None)
