import asyncio
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


class ProfileDocumentInfo(TypedDict):
    file_name: str
    author: str


async def analyze_product_profile_document(
    obj: Object,
) -> ProductProfileDocumentResponse:
    document_name = obj.object_name.split("/")[-1]
    profile_document_info = analyze_profile_document_info(document_name.split(".")[0])
    file_name = profile_document_info["file_name"]
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
    )
    return document


async def get_product_profile_documents(
    product_id: str,
) -> list[ProductProfileDocumentResponse]:
    folder = get_product_profile_folder(product_id)
    objects = await list_objects(folder)
    logger.info(f"Objects: {[o.object_name for o in objects]}")
    documents = [
        analyze_product_profile_document(obj) for obj in objects if obj.is_dir is False
    ]
    documents = await asyncio.gather(*documents)
    # documents = [doc for doc in documents if doc.file_name != "TextInput.txt"]
    return documents


async def get_upload_product_profile_document_url(
    product_id: str,
    profile_document_info: ProfileDocumentInfo,
) -> str:
    extension = profile_document_info["file_name"].split(".")[-1]
    document_name = encode_profile_document_info(profile_document_info)
    document_name = f"{document_name}.{extension}"
    folder = get_product_profile_folder(product_id)
    object_name = f"{folder}/{document_name}"
    url = await generate_put_object_presigned_url(object_name)
    return url


async def delete_product_profile_document(
    product_id: str,
    document_name: str,
) -> None:
    folder = get_product_profile_folder(product_id)
    object_name = f"{folder}/{document_name}"
    await remove_object(object_name)


# ================ FOLDERS ====================


def get_product_profile_folder(
    product_id: str,
) -> str:
    product_folder = get_product_folder(product_id)
    return f"{product_folder}/product_profile"


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
    return document_name


def analyze_profile_document_info(profile_document_info: str) -> ProfileDocumentInfo:
    # urlsafe base64 decode then avro decode
    padding_needed = (-len(profile_document_info)) % 4
    padded_str = profile_document_info + ("=" * padding_needed)
    raw_bytes = base64.urlsafe_b64decode(padded_str)
    buffer = io.BytesIO(raw_bytes)
    profile_document_info = fastavro.schemaless_reader(
        buffer,
        PROFILE_DOCUMENT_INFO_SCHEMA,
    )
    return profile_document_info
