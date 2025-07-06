import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import httpx
from fastapi import HTTPException
from loguru import logger

from src.infrastructure.minio import get_object
from src.infrastructure.openai import get_openai_client
from src.infrastructure.qdrant import search_similar
from src.infrastructure.redis import redis_client
from src.modules.competitive_analysis.model import (
    AnalyzeCompetitiveAnalysisProgress,
    CompetitiveAnalysis,
)
from src.modules.index_system_data.summarize_files import summarize_files
from src.modules.product_profile.schema import ProductProfileDocumentResponse
from src.modules.product_profile.storage import get_product_profile_documents

NUMBER_OF_MANUAL_ANALYSIS = 3
TOTAL_ANALYSIS = 5


class RegulatoryPathway(str, Enum):
    K510 = "510(k)"
    PMA = "PMA"
    DE_NOVO = "De Novo"


class AnalyzeProgress:
    initialized = False
    progress: AnalyzeCompetitiveAnalysisProgress

    async def initialize(self, product_id: str, total_files: int):
        logger.info(
            f"Initializing progress for product_id={product_id}, total_files={total_files}"
        )
        existing_progress = await AnalyzeCompetitiveAnalysisProgress.find_one(
            AnalyzeCompetitiveAnalysisProgress.reference_product_id == product_id,
        )
        if existing_progress:
            logger.info(
                f"Existing progress found for product_id={product_id}, resetting processed_files to 0"
            )
            self.progress = existing_progress
            self.progress.reference_product_id = product_id
            self.progress.total_files = total_files
            self.progress.processed_files = 0
            self.progress.updated_at = datetime.now(timezone.utc)
        else:
            logger.info(
                f"No existing progress found for product_id={product_id}, creating new progress entry"
            )
            self.progress = AnalyzeCompetitiveAnalysisProgress(
                reference_product_id=product_id,
                total_files=total_files,
                processed_files=0,
                updated_at=datetime.now(timezone.utc),
            )
        await self.progress.save()
        self.initialized = True
        logger.info(
            f"Initialized progress for product {product_id} with total files {total_files}"
        )

    async def increase(self, count: int = 1):
        if not self.initialized:
            logger.error("Progress not initialized. Call initialize() first.")
            raise HTTPException(
                status_code=500,
                detail="Progress not initialized. Call initialize() first.",
            )
        logger.info(
            f"Increasing processed_files by {count} for product_id={self.progress.reference_product_id}"
        )
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


async def create_competitive_analysis(
    product_profile_docs: list[ProductProfileDocumentResponse],
    competitor_document_path: Path,
) -> CompetitiveAnalysis:
    logger.info(
        f"Creating competitive analysis. Product profile docs: {[doc.file_name for doc in product_profile_docs]}, Competitor doc: {competitor_document_path}"
    )
    client = get_openai_client()
    uploaded_ids: list[str] = []

    # — your original upload loop for product profiles —
    for doc in product_profile_docs:
        path = Path(f"/tmp/product_profile/{doc.file_name}")
        path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading product profile document from {doc.url} to {path}")
        resp = httpx.get(doc.url)
        resp.raise_for_status()
        path.write_bytes(resp.content)

        with path.open("rb") as f:
            fo = client.files.create(file=f, purpose="assistants")
        logger.info(
            f"Uploaded product profile document {doc.file_name} to OpenAI, file_id={fo.id}"
        )
        uploaded_ids.append(fo.id)

    # — your original download & upload for competitor doc —
    system_data_folder = "system_data"
    key = f"{system_data_folder}/{competitor_document_path.name}"
    logger.info(f"Downloading competitor document from MinIO with key={key}")
    raw_data = await get_object(key)
    competitor_document_path.parent.mkdir(parents=True, exist_ok=True)
    competitor_document_path.write_bytes(raw_data)
    logger.info(f"Saved competitor document to {competitor_document_path}")

    with competitor_document_path.open("rb") as f:
        cfo = client.files.create(file=f, purpose="assistants")
    logger.info(
        f"Uploaded competitor document {competitor_document_path.name} to OpenAI, file_id={cfo.id}"
    )
    uploaded_ids.append(cfo.id)

    # — capture the filenames so we know which is which —
    product_profile_file_names = [
        doc.file_name for doc in product_profile_docs if doc.file_name
    ]
    competitor_file_name = competitor_document_path.name

    # — build the function schema from your Pydantic model —
    func_spec = {
        "name": "create_competitive_analysis",
        "description": "Produce a JSON object matching the CompetitiveAnalysis schema",
        "parameters": CompetitiveAnalysis.schema(),  # Pydantic → JSON Schema
    }

    # — your full instruction string, verbatim —
    instructions = (
        "You are an expert in competitive analysis for medical devices. "
        "You will analyze the provided product profile documents and competitor documents to create a comprehensive competitive analysis. "
        "Your analysis should include the following fields: product_name, reference_number, regulatory_pathway, fda_approved, ce_marked, "
        "is_ai_generated, confidence_score, sources, your_product_summary, competitor_summary of the competitive. "
        "You will receive a list of product profile documents and a competitor document. "
        "The product profile documents will contain information about the product, including its name, reference number, regulatory pathway, "
        "FDA approval status, CE marking status, and other relevant information. "
        "The competitor document will contain information about a competitor's product. "
        "You will analyze the product profile documents and the competitor document to create a competitive analysis. "
        "You will also provide a summary of the product profile and the competitor document. "
        "The competitive analysis should be returned in the CompetitiveAnalysis model format. "
        "If you cannot determine a field, set it to null."
    )

    logger.info("Calling OpenAI chat completion for competitive analysis")
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": json.dumps({
                    "product_profiles": [
                        {"file_name": name, "file_id": fid}
                        for name, fid in zip(
                            product_profile_file_names, uploaded_ids[:-1]
                        )
                    ],
                    "competitor": {
                        "file_name": competitor_file_name,
                        "file_id": uploaded_ids[-1],
                    },
                }),
            },
        ],
        functions=[func_spec],
        function_call={"name": "create_competitive_analysis"},
        temperature=0,
    )

    # — parse the returned JSON into your model —
    args_json = completion.choices[0].message.function_call.arguments
    logger.info(f"Received competitive analysis response from OpenAI: {args_json}")
    analysis = CompetitiveAnalysis.model_validate_json(args_json)
    logger.info(
        f"Competitive analysis parsed successfully for competitor {competitor_file_name}"
    )
    return analysis


async def analyze_competitive_analysis(
    product_id: str,
) -> None:
    logger.info(f"Starting analyze_competitive_analysis for product_id={product_id}")
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeCompetitiveAnalysis:AnalyzeLock:{product_id}",
        timeout=100,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Task is already running for product {product_id}. Skipping analysis."
        )
        return

    paths: list[Path] = []
    docs = await get_product_profile_documents(product_id)
    if not docs:
        logger.info(f"No product profile documents found for product {product_id}.")
        await lock.release()
        return
    logger.info(
        f"Found {len(docs)} product profile documents for product_id={product_id}"
    )
    for doc in docs:
        logger.info(f"Downloading product profile document from {doc.url}")
        response = httpx.get(doc.url)
        temp_path = Path(f"/tmp/product_profile/{doc.file_name}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(response.content)
        logger.info(f"Saved product profile document to {temp_path}")
        paths.append(temp_path)

    # Initialize progress tracking
    progress = AnalyzeProgress()
    await progress.initialize(product_id, total_files=len(docs))

    logger.info(f"Summarizing product profile documents for product_id={product_id}")
    summary = await summarize_files(paths)

    logger.info(
        f"Searching for similar competitor documents for product_id={product_id}"
    )
    similar_docs = search_similar(
        summary,
        2,
    )
    similar_docs_file_names = [
        doc.payload.get("filename", "Unknown") for doc in similar_docs
    ]
    similar_docs_file_names = [i for i in similar_docs_file_names if i != "Unknown"]
    logger.info(f"Found similar competitor documents: {similar_docs_file_names}")
    # download competitor documents
    competitor_documents = [
        Path(f"/tmp/competitor_documents/{name}") for name in similar_docs_file_names
    ]
    competitive_analysis_list: list[CompetitiveAnalysis] = []
    for comp_doc in competitor_documents:
        logger.info(f"Creating competitive analysis for competitor document {comp_doc}")
        competitive_analysis = await create_competitive_analysis(
            product_profile_docs=docs, competitor_document_path=comp_doc
        )
        competitive_analysis.reference_product_id = product_id
        competitive_analysis_list.append(competitive_analysis)

    await CompetitiveAnalysis.find(
        CompetitiveAnalysis.reference_product_id == product_id,
    ).delete_many()
    await CompetitiveAnalysis.insert_many(competitive_analysis_list)
    await progress.complete()

    await lock.release()
    logger.info(f"Released lock for product {product_id}")
