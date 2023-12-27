import aiofiles
import uuid
from typing import IO
from datetime import datetime
from fastapi import UploadFile, HTTPException, status


def get_unique_filename(original_filename: str) -> str:
    unique_id = uuid.uuid4()
    extension = original_filename.split('.')[-1]
    return f"{unique_id}.{extension}"


def validate_file_size(file: IO, file_size: int = 2097152) -> bool:
    real_file_size = 0
    for chunk in file:
        real_file_size += len(chunk)
        if real_file_size > file_size:
            return False
    return True


async def save_file(upload_file: UploadFile, directory: str, filename: str = None) -> str:
    if filename is None:
        filename = get_unique_filename(upload_file.filename)
    file_path = f"{directory}/{filename}"
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return file_path
