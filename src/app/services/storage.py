from src.app.config import settings
import aioboto3


async def upload_file(file_content, filename, content_type) -> str:
    async with aioboto3.Session().client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    ) as s3:
        await s3.put_object(
            Bucket=settings.MINIO_BUCKET,
            Key=filename,
            Body=file_content,
            ContentType=content_type,
        )
        return filename
