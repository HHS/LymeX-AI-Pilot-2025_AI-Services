from datetime import datetime, timezone
from pathlib import Path
import yaml
import os

import httpx
from fastapi import HTTPException
from loguru import logger

from src.infrastructure.redis import redis_client
from src.modules.product_profile.model import (
    ProductProfile,
    AnalyzeProductProfileProgress,
)
from src.modules.product_profile.schema import ProductProfileSchema
from src.modules.product_profile.storage import get_product_profile_documents
from src.utils.extract_documents_data import extract_documents_data


def load_questionnaire_text():
    path = os.path.join("src", "resources", "device_description_questionnaire.yaml")
    with open(path, "r") as f:
        items = yaml.safe_load(f)
    return "\n".join(f"{item['id']}: {item['question']}" for item in items)


class AnalyzeProgress:
    def __init__(self):
        self.progress: AnalyzeProductProfileProgress | None = None

    async def initialize(self, product_id: str, total_files: int):
        existing = await AnalyzeProductProfileProgress.find_one(
            AnalyzeProductProfileProgress.product_id == product_id
        )
        now = datetime.now(timezone.utc)
        if existing:
            existing.total_files = total_files
            existing.processed_files = 0
            existing.updated_at = now
            self.progress = existing
        else:
            self.progress = AnalyzeProductProfileProgress(
                product_id=product_id,
                total_files=total_files,
                processed_files=0,
                updated_at=now,
            )
        await self.progress.save()
        logger.info(f"Progress initialized for {product_id}: {total_files} files")

    async def increment(self, count: int = 1):
        if not self.progress:
            raise HTTPException(500, "Progress must be initialized first.")
        self.progress.processed_files += count
        self.progress.updated_at = datetime.now(timezone.utc)
        await self.progress.save()

    async def complete(self):
        if not self.progress:
            return
        self.progress.processed_files = self.progress.total_files
        self.progress.updated_at = datetime.now(timezone.utc)
        await self.progress.save()
        logger.info(f"Progress complete for {self.progress.product_id}")


async def do_analyze_product_profile(product_id: str) -> None:
    docs = await get_product_profile_documents(product_id)
    total = len(docs)
    progress = AnalyzeProgress()
    await progress.initialize(product_id, total)

    doc_paths: list[Path] = []

    # Upload each document with retry
    for doc in docs:
        async with httpx.AsyncClient() as http_client:
            doc_path = Path("/tmp") / "docs_nois2" / doc.file_name
            doc_paths.append(doc_path)
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            with open(doc_path, "wb") as f:
                response = await http_client.get(doc.url)
                f.write(response.content)

    instruction = (
        "You are an FDA expert. Use the uploaded PDF files to extract a complete "
        "product profile. Return **only** valid JSON that matches the "
        "ProductProfile schema exactly (no explanations or bullet points). "
        "Required fields now include trade name, model number, generic name, "
        "FDA product code, CFR regulation number, storage conditions, shelf-life, "
        "sterility status, warnings, limitations, contraindications, and a "
        "step-by-step instructions-for-use list. Use the literal string "
        "'not available' for any field you cannot confidently extract."
    )
    questionnaire_text = load_questionnaire_text()
    question = (
        "Please extract a complete product profile using all uploaded FDA PDF "
        "documents. In particular:\n"
        "• Determine the FDA regulatory pathway ('510(k)', 'De Novo', or 'Premarket Approval (PMA)').\n"
        "• Capture **trade name, model number, and generic name**.\n"
        "• Capture **FDA product code** and **21 CFR regulation number**.\n"
        "• Capture storage conditions, shelf-life, and sterility status if present.\n"
        "• List any warnings, limitations, or contraindications that appear in labeling.\n"
        "• Any software present, single-use or reprocessed single use device "
        "are there any animal-derived materials in the product \n"
        "• Provide a **step-by-step instructions-for-use** list.\n"
        "If an answer is not found, return the field value as 'not available'.\n\n"
        f"{questionnaire_text}"
    )

    result = await extract_documents_data(
        documents=doc_paths,
        system_instruction=instruction,
        user_question=question,
        model_class=ProductProfileSchema,
    )

    # Save profile
    await ProductProfile.find(ProductProfile.product_id == product_id).delete_many()
    record = {**result.model_dump(), "product_id": product_id}
    await ProductProfile(**record).save()

    await progress.complete()
    logger.success(f"Saved product profile for {product_id}")


async def analyze_product_profile(product_id: str) -> None:
    lock = redis_client.lock(f"analyze_lock:{product_id}", timeout=60)
    if not await lock.acquire(blocking=False):
        logger.warning(f"Analysis already running for {product_id}")
        return

    try:
        await do_analyze_product_profile(product_id)

    except Exception as exc:
        logger.error(f"Error analyzing {product_id}: {exc}")
        raise

    finally:
        try:
            await lock.release()
        except Exception:
            pass
