from src.app.config import settings
from uuid import uuid4
import aioboto3


async def upload_file(file_content, filename, content_type, trip_id) -> str:
    async with aioboto3.Session().client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    ) as s3:
        key = f"trips/{trip_id}/{uuid4()}_{filename}"
        await s3.put_object(
            Bucket=settings.MINIO_BUCKET,
            Key=key,
            Body=file_content,
            ContentType=content_type,
        )
        return key


async def get_file_from_storage(s3_key) -> bytes:
    async with aioboto3.Session().client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    ) as s3:
        response = await s3.get_object(Bucket=settings.MINIO_BUCKET, Key=s3_key)
        content = await response["Body"].read()
        return content


async def delete_file_from_storage(s3_key) -> None:
    async with aioboto3.Session().client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    ) as s3:
        await s3.delete_object(
            Bucket=settings.MINIO_BUCKET,
            Key=s3_key
        )
