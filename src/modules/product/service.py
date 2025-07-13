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
from src.modules.product.storage import (
    analyze_profile_document_info,
    get_product_folder,
    get_product_profile_folder,
)
import base64
import fastavro
import io
from minio.datatypes import Object


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
    return documents
