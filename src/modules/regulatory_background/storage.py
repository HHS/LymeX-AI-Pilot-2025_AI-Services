import asyncio
from typing import TypedDict
import mimetypes
from loguru import logger
from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    list_objects,
)
from src.modules.regulatory_background.schema import (
    RegulatoryBackgroundDocumentResponse,
)
from src.modules.product.storage import get_product_folder
import base64
import fastavro
import io
from minio.datatypes import Object


class BackgroundDocumentInfo(TypedDict):
    file_name: str
    author: str


async def analyze_regulatory_background_document(
    obj: Object,
) -> RegulatoryBackgroundDocumentResponse:
    document_name = obj.object_name.split("/")[-1]
    background_document_info = analyze_background_document_info(
        document_name.split(".")[0]
    )
    file_name = background_document_info["file_name"]
    document = RegulatoryBackgroundDocumentResponse(
        document_name=document_name,
        file_name=file_name,
        url=await generate_get_object_presigned_url(obj.object_name),
        uploaded_at=obj.last_modified.isoformat(),
        author=background_document_info["author"],
        content_type=obj.content_type
        or mimetypes.guess_type(file_name)[0]
        or "application/octet-stream",
        size=obj.size,
        key=obj.object_name,
        path=f"/tmp/{document_name}",
    )
    return document


async def get_regulatory_background_documents(
    product_id: str,
) -> list[RegulatoryBackgroundDocumentResponse]:
    folder = get_regulatory_background_folder(product_id)
    objects = await list_objects(folder)
    logger.info(f"Objects: {[o.object_name for o in objects]}")
    documents = [
        analyze_regulatory_background_document(obj)
        for obj in objects
        if obj.is_dir is False
    ]
    documents = await asyncio.gather(*documents)
    return documents


# ================ FOLDERS ====================


def get_regulatory_background_folder(
    product_id: str,
) -> str:
    product_folder = get_product_folder(product_id)
    return f"{product_folder}/regulatory_background"


# ================ UTILS ====================

REGULATORY_BACKGROUND_DOCUMENT_INFO_SCHEMA = {
    "type": "record",
    "name": "Document",
    "fields": [
        {"name": "file_name", "type": "string"},
        {"name": "author", "type": "string"},
    ],
}


def encode_background_document_info(
    background_document_info: BackgroundDocumentInfo,
) -> str:
    # avro encode then urlsafe base64 encode with no padding
    buffer = io.BytesIO()
    fastavro.schemaless_writer(
        buffer,
        REGULATORY_BACKGROUND_DOCUMENT_INFO_SCHEMA,
        background_document_info,
    )
    raw_bytes = buffer.getvalue()
    encoded = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    document_name = encoded.rstrip("=")
    return document_name


def analyze_background_document_info(
    background_document_info: str,
) -> BackgroundDocumentInfo:
    # urlsafe base64 decode then avro decode
    padding_needed = (-len(background_document_info)) % 4
    padded_str = background_document_info + ("=" * padding_needed)
    raw_bytes = base64.urlsafe_b64decode(padded_str)
    buffer = io.BytesIO(raw_bytes)
    background_document_info = fastavro.schemaless_reader(
        buffer,
        REGULATORY_BACKGROUND_DOCUMENT_INFO_SCHEMA,
    )
    return background_document_info
