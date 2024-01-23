from io import BytesIO
import logging
import os
from aiobotocore import session as aiobotocore
import uuid
from typing import Optional
from starlette.responses import StreamingResponse
from fastapi import Request, UploadFile
from config import settings
from app.common.security import decrypt, encrypt
from config import settings


class FileService:
    def __init__(self, request: Request):
        self.request = request

    def get_unique_filename(self, original_filename: str) -> str:
        unique_id = uuid.uuid4()
        extension = original_filename.split('.')[-1]
        return f"{unique_id}.{extension}"

    async def save_file(self, upload_file: UploadFile, directory: str, filename: Optional[str] = None) -> str:
        if filename is None:
            filename = self.get_unique_filename(upload_file.filename)
        file_path = os.path.join(directory, filename)

        session = aiobotocore.get_session()
        async with session.create_client('s3', region_name=settings.AWS_REGION, 
                                         endpoint_url=settings.AWS_ENDPOINT_URL,
                                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
                                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY) as client:
            await upload_file.seek(0)
            content = await upload_file.read()
            file_stream = BytesIO(content)

            try:
                await client.put_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_path, 
                                        Body=file_stream, ContentType=upload_file.content_type)
            except Exception as e:
                print(f"Error uploading file to S3: {e}")
                raise e
            finally:
                file_stream.close()

        return file_path

    async def fetch_file(self, encrypted_object_name: str) -> Optional[StreamingResponse]:
        try:
            object_name = decrypt(encrypted_object_name)
            session = aiobotocore.get_session()
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return None

        async with session.create_client('s3', region_name=settings.AWS_REGION, 
                                        endpoint_url=settings.AWS_ENDPOINT_URL,
                                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
                                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY) as client:
            try:
                response = await client.get_object(Bucket=settings.AWS_BUCKET_NAME, Key=object_name)
                content_type = response['ResponseMetadata']['HTTPHeaders']['content-type']
                logging.info(f"Content type: {content_type}")
                return StreamingResponse(response['Body'], media_type=content_type)
            except Exception as e:
                logging.error(f"Error fetching file: {e}")
                return None

    async def delete_file(self, object_name: str) -> bool:
        session = aiobotocore.get_session()
        async with session.create_client('s3', region_name=settings.AWS_REGION, 
                                         endpoint_url=settings.AWS_ENDPOINT_URL,
                                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
                                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY) as client:
            try:
                await client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=object_name)
                return True
            except Exception as e:
                print(f"Error deleting file from S3: {e}")
                return False

    def get_url(self, object_name: str):
        encrypted_object_name = encrypt(object_name)
        url = self.request.url_for('file.get_file', encrypted_object_name=encrypted_object_name)
        return str(url)

    # async def create_presigned_url(object_name):
    #     session = aiobotocore.get_session()
    #     async with session.create_client('s3', region_name=settings.AWS_REGION,  # Change to your Spaces region
    #                                      endpoint_url=settings.AWS_ENDPOINT_URL,
    #                                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY) as client:
    #         try:
    #             response = await client.generate_presigned_url('get_object',
    #                                                           Params={'Bucket': settings.AWS_BUCKET_NAME,
    #                                                                   'Key': object_name})
    #             return response
    #         except Exception as e:
    #             print(f"Error generating presigned URL: {e}")
    #             return None


def get_file_service(request: Request):
    return FileService(request)
