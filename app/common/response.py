from typing import Optional, Dict
from fastapi.responses import JSONResponse
from app.schemas import StandardResponse, T


def standard_response(
    status: int,
    message: str,
    result: Optional[T] = None,
    headers: Optional[Dict[str, str]] = None
) -> StandardResponse[T]:
    content = StandardResponse[T](status=status, message=message, result=result).model_dump()
    return JSONResponse(content=content, status_code=status, headers=headers)