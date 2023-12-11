from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any

app = FastAPI()


class StandardResponse(BaseModel):
    status: int
    message: str
    result: Optional[Any] = None


def standard_response(status, message, result=None):
    return StandardResponse(status=status, message=message, result=result)
