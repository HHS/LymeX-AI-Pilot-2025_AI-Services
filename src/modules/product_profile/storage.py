from pathlib import Path
from typing import TypedDict
import mimetypes
from loguru import logger
from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
    list_objects,
    remove_object,
)
from src.modules.product_profile.schema import (
    ProductProfileDocumentResponse,
)
from src.modules.product.storage import get_product_folder
import base64
import fastavro
import io
from minio.datatypes import Object

from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent
from src.utils.download_minio_files import download_minio_file


class ProfileDocumentInfo(TypedDict):
    file_name: str
    author: str


async def parse_product_profile_document(
    obj: Object,
) -> ProductProfileDocumentResponse:
    document_name = obj.object_name.split("/")[-1]
    logger.info(f"Parsing document: {document_name}")
    profile_document_info = parse_profile_document_info(document_name.split(".")[0])
    file_name = profile_document_info["file_name"]
    logger.info(f"Profile document info: {profile_document_info}")
    path = await download_minio_file(obj.object_name)
    logger.info(f"Downloaded file to: {path}")

    document = ProductProfileDocumentResponse(
        document_name=document_name,
        file_name=file_name,
        url=await generate_get_object_presigned_url(obj.object_name),
        uploaded_at=obj.last_modified.isoformat(),
        author=profile_document_info["author"],
        content_type=obj.content_type
        or mimetypes.guess_type(file_name)[0]
        or "application/octet-stream",
        size=obj.size,
        key=obj.object_name,
        path=path.as_posix(),
    )
    logger.info(f"Parsed document response: {document}")
    return document


async def get_product_profile_documents(
    product_id: str,
) -> list[ProductProfileDocumentResponse]:
    logger.info(f"Getting product profile documents for product_id: {product_id}")
    folder = get_product_profile_folder(product_id)
    logger.info(f"Product profile folder: {folder}")
    objects = await list_objects(folder)
    logger.info(f"Objects found: {[o.object_name for o in objects]}")
    parse_product_profile_document_tasks = [
        parse_product_profile_document(obj) for obj in objects if obj.is_dir is False
    ]
    documents = await async_gather_with_max_concurrent(
        parse_product_profile_document_tasks,
    )
    logger.info(f"Retrieved {len(documents)} product profile documents")
    return documents


async def get_upload_product_profile_document_url(
    product_id: str,
    profile_document_info: ProfileDocumentInfo,
) -> str:
    logger.info(
        f"Generating upload URL for product_id: {product_id}, info: {profile_document_info}"
    )
    extension = profile_document_info["file_name"].split(".")[-1]
    document_name = encode_profile_document_info(profile_document_info)
    document_name = f"{document_name}.{extension}"
    folder = get_product_profile_folder(product_id)
    object_name = f"{folder}/{document_name}"
    logger.info(f"Upload object name: {object_name}")
    url = await generate_put_object_presigned_url(object_name)
    logger.info(f"Generated upload URL: {url}")
    return url


async def delete_product_profile_document(
    product_id: str,
    document_name: str,
) -> None:
    logger.info(
        f"Deleting product profile document: {document_name} for product_id: {product_id}"
    )
    folder = get_product_profile_folder(product_id)
    object_name = f"{folder}/{document_name}"
    logger.info(f"Object name to delete: {object_name}")
    await remove_object(object_name)
    logger.info(f"Deleted object: {object_name}")


# ================ FOLDERS ====================


def get_product_profile_folder(
    product_id: str,
) -> str:
    product_folder = get_product_folder(product_id)
    folder = f"{product_folder}/product_profile"
    logger.info(f"Product profile folder for product_id {product_id}: {folder}")
    return folder


# ================ UTILS ====================

PROFILE_DOCUMENT_INFO_SCHEMA = {
    "type": "record",
    "name": "Document",
    "fields": [
        {"name": "file_name", "type": "string"},
        {"name": "author", "type": "string"},
    ],
}


def encode_profile_document_info(profile_document_info: ProfileDocumentInfo) -> str:
    logger.info(f"Encoding profile document info: {profile_document_info}")
    # avro encode then urlsafe base64 encode with no padding
    buffer = io.BytesIO()
    fastavro.schemaless_writer(
        buffer,
        PROFILE_DOCUMENT_INFO_SCHEMA,
        profile_document_info,
    )
    raw_bytes = buffer.getvalue()
    encoded = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    document_name = encoded.rstrip("=")
    logger.info(f"Encoded document name: {document_name}")
    return document_name


def parse_profile_document_info(profile_document_info: str) -> ProfileDocumentInfo:
    logger.info(f"Parsing profile document info from string: {profile_document_info}")
    # urlsafe base64 decode then avro decode
    padding_needed = (-len(profile_document_info)) % 4
    padded_str = profile_document_info + ("=" * padding_needed)
    raw_bytes = base64.urlsafe_b64decode(padded_str)
    buffer = io.BytesIO(raw_bytes)
    profile_document_info = fastavro.schemaless_reader(
        buffer,
        PROFILE_DOCUMENT_INFO_SCHEMA,
    )
    logger.info(f"Decoded profile document info: {profile_document_info}")
    return profile_document_info
