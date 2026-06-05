import os
import uuid
from io import BytesIO

import boto3
from botocore.client import Config

MINIO_ENDPOINT   = os.getenv("MINIO_ENDPOINT",   "minio.warlockcode.com")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY",  "grimorio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY",  "")
MINIO_BUCKET     = os.getenv("MINIO_BUCKET",      "aguacatia")
MINIO_SECURE     = os.getenv("MINIO_SECURE", "true").lower() == "true"

_s3 = None


def _get_client():
    global _s3
    if _s3 is None:
        protocol = "https" if MINIO_SECURE else "http"
        _s3 = boto3.client(
            "s3",
            endpoint_url=f"{protocol}://{MINIO_ENDPOINT}",
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        _ensure_bucket(_s3)
    return _s3


def _ensure_bucket(client):
    try:
        client.head_bucket(Bucket=MINIO_BUCKET)
    except Exception:
        client.create_bucket(Bucket=MINIO_BUCKET)
        # Hacer el bucket público de lectura
        policy = f"""{{
            "Version":"2012-10-17",
            "Statement":[{{
                "Effect":"Allow",
                "Principal":"*",
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::{MINIO_BUCKET}/*"]
            }}]
        }}"""
        client.put_bucket_policy(Bucket=MINIO_BUCKET, Policy=policy)


def upload_image(image_bytes: bytes, content_type: str = "image/jpeg") -> str:
    """Sube imagen a MinIO y retorna la URL pública."""
    client = _get_client()
    key = f"clasificaciones/{uuid.uuid4()}.jpg"

    client.put_object(
        Bucket=MINIO_BUCKET,
        Key=key,
        Body=BytesIO(image_bytes),
        ContentType=content_type,
        ContentLength=len(image_bytes),
    )

    protocol = "https" if MINIO_SECURE else "http"
    return f"{protocol}://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{key}"
