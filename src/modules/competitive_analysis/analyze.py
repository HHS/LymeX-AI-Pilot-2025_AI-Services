from datetime import datetime, timezone
from enum import Enum
from random import choice, randint, sample
from src.infrastructure.redis import redis_client
from fastapi import HTTPException
from loguru import logger
from src.modules.competitive_analysis.model import (
    AnalyzeCompetitiveAnalysisProgress,
    CompetitiveAnalysis,
)
from src.modules.competitive_analysis.schema import (
    CompetitiveAnalysisCompareSummary,
    CompetitiveDeviceAnalysisKeyDifferenceResponse,
)
from src.modules.competitive_analysis.storage import get_competitive_analysis_documents
from src.modules.product_profile.schema import Performance

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


async def analyze_competitive_analysis(
    product_id: str,
) -> None:
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

    documents = await get_competitive_analysis_documents(product_id)
    # Randomly pick documents to analyze
    number_of_manual_analysis = min(
        NUMBER_OF_MANUAL_ANALYSIS,
        len(documents),
    )
    documents = sample(documents, number_of_manual_analysis)
    number_of_ai_generation = TOTAL_ANALYSIS - number_of_manual_analysis
    competitive_analysis_list: list[CompetitiveAnalysis] = []
    progress = AnalyzeProgress()
    await progress.initialize(
        product_id=product_id,
        total_files=TOTAL_ANALYSIS,
    )
    logger.info("Starting analysis of competitive analysis documents...")
    for i, document in enumerate(documents):
        product_name = f"Test Product {document.document_name}"
        competitive_analysis = CompetitiveAnalysis(
            reference_product_id=product_id,
            product_name=product_name,
            category=document.category,
            regulatory_pathway=document.category,
            clinical_study="clinical_study",
            fda_approved=True,
            ce_marked=True,
            device_ifu_description="Device IFU description",
            key_differences=[
                CompetitiveDeviceAnalysisKeyDifferenceResponse(
                    title="Patient Population",
                    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    icon="https://example.com/icon1.png",
                ),
                CompetitiveDeviceAnalysisKeyDifferenceResponse(
                    title="Usage Environment",
                    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    icon="https://example.com/icon2.png",
                ),
                CompetitiveDeviceAnalysisKeyDifferenceResponse(
                    title="Certifications",
                    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    icon="https://example.com/icon3.png",
                ),
            ],
            recommendations=[
                "Recommendation 1",
                "Recommendation 2",
                "Recommendation 3",
            ],
            is_ai_generated=False,
            features=[
                {
                    "name": "Feature 1",
                    "description": "Description of feature 1",
                },
                {
                    "name": "Feature 2",
                    "description": "Description of feature 2",
                },
                {
                    "name": "Feature 3",
                    "description": "Description of feature 3",
                },
            ],
            claims=[
                "Claim 1",
                "Claim 2",
                "Claim 3",
            ],
            reference_number=f"Reference Number {randint(1, 1000000)}",
            confidence_score=randint(1, 100) / 100,
            sources=[document.url],
            performance=Performance(
                speed=randint(50, 100),
                reliability=randint(50, 100),
            ),
            price=randint(1000, 5000),
            your_product_summary=CompetitiveAnalysisCompareSummary(
                title="Your Product Summary",
                summary="This is a summary of your product's competitive analysis.",
                icon="https://example.com/your-product-icon.png",
            ),
            competitor_summary=CompetitiveAnalysisCompareSummary(
                title="Competitor Summary",
                summary="This is a summary of the competitor's product.",
                icon="https://example.com/competitor-icon.png",
            ),
            instructions=[
                "Follow the instructions provided in the document.",
                "Ensure compliance with regulatory standards.",
                "Review the key differences highlighted in the analysis.",
            ],
            type_of_use="prescription",
        )
        competitive_analysis_list.append(competitive_analysis)
        await progress.increase()
        logger.info(
            f"Analyzed competitive analysis document {i + 1}/{number_of_manual_analysis} for product: {product_id}"
        )
    logger.info("Starting AI generation of competitive analysis...")
    for _ in range(number_of_ai_generation):
        competitive_analysis = CompetitiveAnalysis(
            reference_product_id=product_id,
            product_name=f"Test Product {randint(1, 1000000)}",
            category=choice(list(RegulatoryPathway)),
            regulatory_pathway=choice(list(RegulatoryPathway)),
            clinical_study="clinical_study",
            fda_approved=True,
            ce_marked=True,
            device_ifu_description="Device IFU description",
            key_differences=[
                CompetitiveDeviceAnalysisKeyDifferenceResponse(
                    title="Patient Population",
                    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    icon="https://example.com/icon1.png",
                ),
                CompetitiveDeviceAnalysisKeyDifferenceResponse(
                    title="Usage Environment",
                    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    icon="https://example.com/icon2.png",
                ),
                CompetitiveDeviceAnalysisKeyDifferenceResponse(
                    title="Certifications",
                    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    icon="https://example.com/icon3.png",
                ),
            ],
            recommendations=[
                "Recommendation 1",
                "Recommendation 2",
                "Recommendation 3",
            ],
            is_ai_generated=True,
            features=[
                {
                    "name": "Feature 1",
                    "description": "Description of feature 1",
                },
                {
                    "name": "Feature 2",
                    "description": "Description of feature 2",
                },
                {
                    "name": "Feature 3",
                    "description": "Description of feature 3",
                },
            ],
            claims=[
                "Claim 1",
                "Claim 2",
                "Claim 3",
            ],
            reference_number=f"Reference Number {randint(1, 1000000)}",
            confidence_score=randint(1, 100) / 100,
            sources=[
                "https://example.com/ai-generated-source-1",
                "https://example.com/ai-generated-source-2",
                "https://example.com/ai-generated-source-3",
                "https://example.com/ai-generated-source-4",
                "https://example.com/ai-generated-source-5",
            ],
            performance=Performance(
                speed=randint(50, 100),
                reliability=randint(50, 100),
            ),
            price=randint(1000, 5000),
            your_product_summary=CompetitiveAnalysisCompareSummary(
                title="Your Product Summary",
                summary="This is a summary of your product's competitive analysis.",
                icon="https://example.com/your-product-icon.png",
            ),
            competitor_summary=CompetitiveAnalysisCompareSummary(
                title="Competitor Summary",
                summary="This is a summary of the competitor's product.",
                icon="https://example.com/competitor-icon.png",
            ),
            instructions=[
                "Follow the instructions provided in the document.",
                "Ensure compliance with regulatory standards.",
                "Review the key differences highlighted in the analysis.",
            ],
            type_of_use="prescription",
        )
        competitive_analysis_list.append(competitive_analysis)
        await progress.increase()
        logger.info(
            f"Generated AI competitive analysis {len(competitive_analysis_list)}/{number_of_ai_generation} for product: {product_id}"
        )
    logger.info(f"Finished analyzing competitive analysis for product: {product_id}")
    await CompetitiveAnalysis.find(
        CompetitiveAnalysis.reference_product_id == product_id,
    ).delete_many()
    await CompetitiveAnalysis.insert_many(competitive_analysis_list)
    logger.info(
        f"Analyzed {len(competitive_analysis_list)} competitive analysis for product: {product_id}, including {number_of_manual_analysis} manual analysis and {number_of_ai_generation} AI-generated analysis."
    )
    await lock.release()
    logger.info(f"Released lock for product {product_id}")
