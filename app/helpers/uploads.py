import aiofiles
import uuid
from datetime import datetime
from fastapi import UploadFile


def get_unique_filename(original_filename: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4()
    extension = original_filename.split('.')[-1]
    return f"{timestamp}_{unique_id}.{extension}"


async def save_file(upload_file: UploadFile, directory: str, filename: str = None) -> str:
    if filename is None:
        filename = get_unique_filename(upload_file.filename)
    file_path = f"{directory}/{filename}"
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return file_path
