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
from src.modules.competitive_analysis.schema import (
    CompetitiveAnalysisDocumentResponse,
)
from src.modules.product.storage import get_product_folder
import base64
import fastavro
import io
from minio.datatypes import Object


class AnalysisDocumentInfo(TypedDict):
    file_name: str
    author: str
    product_name: str


async def analyze_competitive_analysis_document(
    obj: Object,
) -> CompetitiveAnalysisDocumentResponse:
    document_name = obj.object_name.split("/")[-1]
    analysis_document_info = analyze_analysis_document_info(document_name.split(".")[0])
    file_name = analysis_document_info["file_name"]
    document = CompetitiveAnalysisDocumentResponse(
        document_name=document_name,
        file_name=file_name,
        url=await generate_get_object_presigned_url(obj.object_name),
        product_name=analysis_document_info["product_name"],
        uploaded_at=obj.last_modified.isoformat(),
        author=analysis_document_info["author"],
        content_type=obj.content_type
        or mimetypes.guess_type(file_name)[0]
        or "application/octet-stream",
        size=obj.size,
    )
    return document


async def get_competitive_analysis_documents(
    product_id: str,
) -> list[CompetitiveAnalysisDocumentResponse]:
    folder = get_competitive_analysis_folder(product_id)
    objects = await list_objects(folder)
    logger.info(f"Objects: {[o.object_name for o in objects]}")
    documents = [
        analyze_competitive_analysis_document(obj)
        for obj in objects
        if obj.is_dir is False
    ]
    documents = await asyncio.gather(*documents)
    return documents


async def get_upload_competitive_analysis_document_url(
    product_id: str,
    analysis_document_info: AnalysisDocumentInfo,
) -> str:
    extension = analysis_document_info["file_name"].split(".")[-1]
    document_name = encode_analysis_document_info(analysis_document_info)
    document_name = f"{document_name}.{extension}"
    folder = get_competitive_analysis_folder(product_id)
    object_name = f"{folder}/{document_name}"
    url = await generate_put_object_presigned_url(object_name)
    return url


async def delete_competitive_analysis_document(
    product_id: str,
    document_name: str,
) -> None:
    folder = get_competitive_analysis_folder(product_id)
    object_name = f"{folder}/{document_name}"
    await remove_object(object_name)


# ================ FOLDERS ====================


def get_competitive_analysis_folder(
    product_id: str,
) -> str:
    product_folder = get_product_folder(product_id)
    return f"{product_folder}/competitive_analysis"


# ================ UTILS ====================

ANALYSIS_DOCUMENT_INFO_SCHEMA = {
    "type": "record",
    "name": "Document",
    "fields": [
        {"name": "file_name", "type": "string"},
        {"name": "author", "type": "string"},
        {"name": "product_name", "type": "string"},
    ],
}


def encode_analysis_document_info(analysis_document_info: AnalysisDocumentInfo) -> str:
    # avro encode then urlsafe base64 encode with no padding
    buffer = io.BytesIO()
    fastavro.schemaless_writer(
        buffer,
        ANALYSIS_DOCUMENT_INFO_SCHEMA,
        analysis_document_info,
    )
    raw_bytes = buffer.getvalue()
    encoded = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    document_name = encoded.rstrip("=")
    return document_name


def analyze_analysis_document_info(analysis_document_info: str) -> AnalysisDocumentInfo:
    # urlsafe base64 decode then avro decode
    padding_needed = (-len(analysis_document_info)) % 4
    padded_str = analysis_document_info + ("=" * padding_needed)
    raw_bytes = base64.urlsafe_b64decode(padded_str)
    buffer = io.BytesIO(raw_bytes)
    analysis_document_info = fastavro.schemaless_reader(
        buffer,
        ANALYSIS_DOCUMENT_INFO_SCHEMA,
    )
    return analysis_document_info
