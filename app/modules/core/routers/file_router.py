from typing import Optional
from fastapi import APIRouter, Depends
from app.modules.core.services.file_service import FileService, get_file_service
from app.common.response import standard_response

router = APIRouter()


@router.get(
    "/files/{encrypted_object_name}",
    name="file.get_file",
)
async def get_file(
    encrypted_object_name: Optional[str],
    file_service: FileService = Depends(get_file_service)
):
    res = await file_service.fetch_file(encrypted_object_name)
    if res:
        return res

    return standard_response(404, "File not found", None)