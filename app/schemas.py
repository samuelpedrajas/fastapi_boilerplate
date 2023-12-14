from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any

class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(...)
    msg: str = Field(...)
    type: str = Field(...)
    input: str = Field(None)
    ctx: Dict[str, Any] = Field(None)
