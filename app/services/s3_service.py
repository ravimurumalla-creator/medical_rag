from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings


class S3Service:
    def __init__(self):
        self.settings = get_settings()
        self.client = boto3.client(
            "s3",
            region_name=self.settings.AWS_REGION,
        )
        self.bucket_name = self.settings.S3_BUCKET_NAME

    def upload_file(self, file_path: Path, object_name: str | None = None) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        key = object_name or file_path.name

        try:
            self.client.upload_file(
                Filename=str(file_path),
                Bucket=self.bucket_name,
                Key=key,
            )
        except ClientError as e:
            raise RuntimeError(f"S3 upload failed: {str(e)}") from e

        return key

    def upload_bytes(self, data: bytes, object_name: str, content_type: str | None = None) -> str:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
                **extra_args,
            )
        except ClientError as e:
            raise RuntimeError(f"S3 byte upload failed: {str(e)}") from e

        return object_name

    def build_s3_uri(self, object_name: str) -> str:
        return f"s3://{self.bucket_name}/{object_name}"
    