import asyncio
import json
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path

import httpx
from fastapi import HTTPException
from loguru import logger
from openai import OpenAIError

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
        existing_progress = await AnalyzeCompetitiveAnalysisProgress.find_one(
            AnalyzeCompetitiveAnalysisProgress.reference_product_id == product_id,
        )
        if existing_progress:
            self.progress = existing_progress
            self.progress.reference_product_id = product_id
            self.progress.total_files = total_files
            self.progress.processed_files = 0
            self.progress.updated_at = datetime.now(timezone.utc)
        else:
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
            raise HTTPException(
                status_code=500,
                detail="Progress not initialized. Call initialize() first.",
            )
        self.progress.processed_files += count
        self.progress.updated_at = datetime.now(timezone.utc)
        await self.progress.save()


async def create_competitive_analysis(
    product_profile_docs: list[ProductProfileDocumentResponse],
    competitor_document_path: Path,
) -> CompetitiveAnalysis:
    client = get_openai_client()
    uploaded_ids: list[str] = []

    # — your original upload loop for product profiles —
    for doc in product_profile_docs:
        path = Path(f"/tmp/product_profile/{doc.file_name}")
        path.parent.mkdir(parents=True, exist_ok=True)

        resp = httpx.get(doc.url)
        resp.raise_for_status()
        path.write_bytes(resp.content)

        with path.open("rb") as f:
            fo = client.files.create(file=f, purpose="assistants")
        uploaded_ids.append(fo.id)

    # — your original download & upload for competitor doc —
    system_data_folder = "system_data"
    key = f"{system_data_folder}/{competitor_document_path.name}"
    raw_data = await get_object(key)
    competitor_document_path.parent.mkdir(parents=True, exist_ok=True)
    competitor_document_path.write_bytes(raw_data)

    with competitor_document_path.open("rb") as f:
        cfo = client.files.create(file=f, purpose="assistants")
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
        "is_ai_generated, confidence_score, sources, your_product_summary, competitor_summary. "
        "You will receive a list of product profile documents and a competitor document. "
        "The product profile documents will contain information about the product, including its name, reference number, regulatory pathway, "
        "FDA approval status, CE marking status, and other relevant information. "
        "The competitor document will contain information about a competitor's product. "
        "You will analyze the product profile documents and the competitor document to create a competitive analysis. "
        "You will also provide a summary of the product profile and the competitor document. "
        "The competitive analysis should be returned in the CompetitiveAnalysis model format. "
        "If you cannot determine a field, set it to null."
    )

    # — call the chat completion with function-calling, including your instructions —
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
    analysis = CompetitiveAnalysis.model_validate_json(args_json)
    return analysis


async def analyze_competitive_analysis(
    product_id: str,
) -> None:
    # lock = redis_client.lock(
    #     f"NOIS2:Background:AnalyzeCompetitiveAnalysis:AnalyzeLock:{product_id}",
    #     timeout=100,
    # )
    # lock_acquired = await lock.acquire(blocking=False)
    # if not lock_acquired:
    #     logger.info(
    #         f"Task is already running for product {product_id}. Skipping analysis."
    #     )
    #     return

    paths: list[Path] = []
    docs = await get_product_profile_documents(product_id)
    for doc in docs:
        response = httpx.get(doc.url)
        temp_path = Path(f"/tmp/product_profile/{doc.file_name}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(response.content)
        paths.append(temp_path)
    summary = await summarize_files(paths)

    similar_docs = search_similar(
        summary,
        2,
    )
    print("+++++++++++++++++++++++")
    print(similar_docs)
    similar_docs_file_names = [
        doc.payload.get("filename", "Unknown") for doc in similar_docs
    ]
    similar_docs_file_names = [i for i in similar_docs_file_names if i != "Unknown"]
    # download competitor documents
    competitor_documents = [
        Path(f"/tmp/competitor_documents/{name}") for name in similar_docs_file_names
    ]
    for comp_doc in competitor_documents:
        competitive_analysis = await create_competitive_analysis(
            product_profile_docs=docs, competitor_document_path=comp_doc
        )
        print("=======================")
        print(competitive_analysis.model_dump_json(indent=4))

    # await lock.release()
    # logger.info(f"Released lock for product {product_id}")
