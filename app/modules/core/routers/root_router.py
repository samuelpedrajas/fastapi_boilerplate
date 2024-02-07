from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse('storage/static/favicon.ico')
