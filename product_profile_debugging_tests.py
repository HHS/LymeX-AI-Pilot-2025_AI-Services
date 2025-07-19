# tests/test_product_profile_with_MongoDB.py
#
# End‑to‑end smoke‑test for the Product‑Profile pipeline:
#   1. Upload one (or more) product‑profile PDFs to MinIO via a presigned URL
#   2. Run analyze_product_profile() so the assistant ingests the PDFs
#   3. Print / verify what was persisted to MongoDB
#
# Usage:  python -m pytest -q tests/test_product_profile_with_MongoDB.py
#         or simply  python tests/test_product_profile_with_MongoDB.py

import os
import asyncio
import mimetypes
import httpx
from unittest.mock import patch

# ─── 1  Runtime‑environment variables ────────────────────────────
# os.environ.update(
#     MONGO_URI="mongodb://localhost:27017",
#     MONGO_DB="dummy",
#     REDIS_HOST="localhost",
#     REDIS_PORT="6379",
#     REDIS_DB="0",
#     MINIO_INTERNAL_ENDPOINT="https://s3.us-west-2.amazonaws.com",
#     MINIO_ROOT_USER="MINIO_ROOT_USER_PLACEHOLDER",
#     MINIO_ROOT_PASSWORD="MINIO_ROOT_PASSWORD_PLACEHOLDER",
#     MINIO_BUCKET="nois2-192-dev",
#     OPENAI_API_KEY="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",
# )

# ─── 2  Imports AFTER env vars are set ───────────────────────────
import motor.motor_asyncio
import beanie
from src.modules.product_profile.model import (
    ProductProfile,
    AnalyzeProductProfileProgress,
)
from src.modules.product_profile.storage import get_upload_product_profile_document_url
from src.modules.product_profile.analyze import analyze_product_profile


# ─── 3  Mongo / Beanie initialisation ───────────────────────────
async def init_beanie() -> None:
    client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URI"])
    await beanie.init_beanie(
        database=client[os.environ["MONGO_DB"]],
        document_models=[ProductProfile, AnalyzeProductProfileProgress],
    )


# ─── 4  Helper: PUT a local file to a presigned URL ─────────────
async def put_to_presigned(url: str, local_path: str) -> None:
    ctype = mimetypes.guess_type(local_path)[0] or "application/pdf"
    async with httpx.AsyncClient() as client:
        with open(local_path, "rb") as fh:
            await client.put(url, content=fh.read(), headers={"Content-Type": ctype})


# ─── 5  Dummy Redis lock (use real Redis in CI) ─────────────────
class DummyLock:
    async def acquire(self, blocking=False):
        return True

    async def release(self):
        return True


# ─── 6  Main coroutine ──────────────────────────────────────────
async def main() -> None:
    await init_beanie()

    product_id = "TEST-PP-001"  # use a unique id for every run

    # ① Upload PDF(s) to MinIO
    for pdf_path in [
        "/Users/macbookpro/Downloads/IVD Dummy Device Description.docx"
        # r"C:/path/to/another_profile_doc.pdf",
    ]:
        presigned = await get_upload_product_profile_document_url(
            product_id,
            {"file_name": os.path.basename(pdf_path), "author": "Yishu"},
        )
        await put_to_presigned(presigned, pdf_path)

    # ② Kick off the product‑profile extraction
    with patch(
        "src.modules.product_profile.analyze.redis_client.lock",
        return_value=DummyLock(),
    ):
        await analyze_product_profile(product_id)

    # ③ Inspect what got stored
    profile = await ProductProfile.find_one({"product_id": product_id})
    if profile:
        print(
            "📝 Stored product‑profile:\n",
            profile.model_dump_json(indent=2, by_alias=True),
        )
    else:
        print("⚠️  No ProductProfile record found!")


if __name__ == "__main__":
    asyncio.run(main())
