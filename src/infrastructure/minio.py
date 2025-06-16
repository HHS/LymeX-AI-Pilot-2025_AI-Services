import asyncio
from datetime import timedelta
from fastapi import FastAPI
from minio import Minio
from minio.datatypes import Object
from src.environment import environment

app = FastAPI()

minio_client = Minio(
    environment.minio_internal_endpoint.removeprefix("http://").removeprefix(
        "https://"
    ),
    access_key=environment.minio_root_user,
    secret_key=environment.minio_root_password,
    secure=environment.minio_internal_endpoint.startswith("https://"),
)


async def generate_put_object_presigned_url(
    object_name: str,
    expiration_seconds=300,
) -> str:
    put_object_presigned_url = await asyncio.to_thread(
        minio_client.presigned_put_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
        expires=timedelta(seconds=expiration_seconds),
    )
    return put_object_presigned_url


async def generate_get_object_presigned_url(
    object_name: str,
    expiration_seconds=300,
) -> str:
    get_object_presigned_url = await asyncio.to_thread(
        minio_client.presigned_get_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
        expires=timedelta(seconds=expiration_seconds),
    )
    return get_object_presigned_url


async def list_objects(prefix: str, recursive=False) -> list[Object]:
    if not prefix.endswith("/"):
        prefix += "/"
    objects = await asyncio.to_thread(
        minio_client.list_objects,
        bucket_name=environment.minio_bucket,
        prefix=prefix,
        recursive=recursive,
    )
    return list(objects)


async def remove_object(object_name: str) -> None:
    await asyncio.to_thread(
        minio_client.remove_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
    )


async def get_object(object_name: str) -> bytes:
    data = await asyncio.to_thread(
        minio_client.get_object,
        bucket_name=environment.minio_bucket,
        object_name=object_name,
    )
    return data.read()
