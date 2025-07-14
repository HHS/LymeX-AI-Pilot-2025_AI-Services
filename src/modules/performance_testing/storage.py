from __future__ import annotations

import asyncio, base64, io, mimetypes
from typing import TypedDict, Literal, Optional

import fastavro
import json
from loguru import logger
from minio.datatypes import Object

from src.infrastructure.minio import (
    generate_get_object_presigned_url,
    generate_put_object_presigned_url,
    list_objects,
    remove_object,
)
from src.modules.product.storage import get_product_folder
from src.modules.performance_testing.schema import PerformanceTestingSection   # tiny enum you add
from src.modules.performance_testing.schema import PerfTestingDocumentResponse  # 1-field Pydantic model


# ──────────────────────────── Avro schema ───────────────────────────
PERF_DOC_INFO_SCHEMA = {
    "type": "record",
    "name": "PerfDoc",
    "fields": [
        {"name": "file_name", "type": "string"},
        {"name": "author",    "type": "string"},
    ],
}

class PerfDocInfo(TypedDict):
    file_name: str
    author: str


# ───────────────────── name-encoding helpers ──────────────────────
def _encode_info(info: dict[str, str]) -> str:
    """
    Embed JSON metadata inside the object-name.

    We base64-encode the JSON so the result stays filename-safe
    (only letters, digits, +, /, =), then strip '=' padding and
    replace '/' by '_' to avoid path separators.
    """
    raw = json.dumps(info, separators=(",", ":")).encode()
    b64 = base64.urlsafe_b64encode(raw).decode().rstrip("=")  # url-safe, no padding
    return b64

def _decode_info(stem: str) -> dict[str, str]:
    """
    Reverse of `_encode_info`.
    """
    # restore padding (multiple of 4)
    padded = stem + "=" * ((4 - len(stem) % 4) % 4)
    raw = base64.urlsafe_b64decode(padded.encode())
    return json.loads(raw)

# ─────────────────── folder helpers ──────────────────────────
def _perf_root(product_id: str) -> str:
    return f"{get_product_folder(product_id)}/performance_testing"

# ─────────────────── CRUD helpers  ───────────────────────────
async def get_performance_testing_documents(product_id: str) -> list[PerfTestingDocumentResponse]:
    """Return **all** performance-testing docs (flat folder)."""
    objs = await list_objects(_perf_root(product_id))
    logger.info(f"Objects: {[o.object_name for o in objs]}")
    tasks = [_obj_to_response(o) for o in objs if not o.is_dir]
    return await asyncio.gather(*tasks)

async def _obj_to_response(obj: Object) -> PerfTestingDocumentResponse:
    name = obj.object_name.split("/")[-1]
    info = _decode_info(name.split(".")[0])

    return PerfTestingDocumentResponse(
        document_name = name,
        file_name     = info["file_name"],
        author        = info["author"],
        url           = await generate_get_object_presigned_url(obj.object_name),
        uploaded_at   = obj.last_modified.isoformat(),
        content_type  = obj.content_type or mimetypes.guess_type(info["file_name"])[0] or "application/octet-stream",
        size          = obj.size,
    )

async def get_upload_performance_testing_document_url(
    product_id: str,
    info: PerfDocInfo,
) -> str:
    ext  = info["file_name"].split(".")[-1]
    name = f"{_encode_info(info)}.{ext}"
    path = f"{_perf_root(product_id)}/{name}"
    return await generate_put_object_presigned_url(path)

async def delete_performance_testing_document(
    product_id: str,
    document_name: str,
) -> None:
    await remove_object(f"{_perf_root(product_id)}/{document_name}")
