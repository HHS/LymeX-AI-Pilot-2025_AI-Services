from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from src.environment import environment
from src.modules.checklist.model import AnalyzeChecklistProgress, Checklist
from src.modules.claim_builder.model import (
    AnalyzeClaimBuilderProgress,
    ClaimBuilder,
)
from src.modules.clinical_trial.model import ClinicalTrial
from src.modules.competitive_analysis.model import (
    AnalyzeCompetitiveAnalysisProgress,
    CompetitiveAnalysis,
    CompetitiveAnalysisDetail,
)
from src.modules.performance_testing.model import (
    AnalyzePerformanceTestingProgress,
    PerformanceTesting,
    PredicateLLMAnalysis,
)
from src.modules.performance_testing.plan_model import PerformanceTestPlan
from src.modules.product.model import Product
from src.modules.product_profile.model import (
    AnalyzeProductProfileProgress,
    ProductProfile,
)
from src.modules.regulatory_background.model import (
    AnalyzeRegulatoryBackgroundProgress,
    RegulatoryBackground,
)
from src.modules.regulatory_pathway.model import (
    AnalyzeRegulatoryPathwayProgress,
    RegulatoryPathway,
)
from src.modules.test_comparison.model import (
    TestComparison,
)

client = AsyncIOMotorClient(environment.mongo_uri)
db = client[environment.mongo_db]


async def init_db() -> None:
    logger.info("Initializing database connection...")
    await init_beanie(
        database=db,
        document_models=[
            Product,
            CompetitiveAnalysis,
            CompetitiveAnalysisDetail,
            AnalyzeCompetitiveAnalysisProgress,
            ProductProfile,
            AnalyzeProductProfileProgress,
            ClaimBuilder,
            AnalyzeClaimBuilderProgress,
            PerformanceTesting,
            PredicateLLMAnalysis,
            TestComparison,
            ClinicalTrial,
            RegulatoryPathway,
            AnalyzeRegulatoryPathwayProgress,
            PerformanceTestPlan,
            AnalyzePerformanceTestingProgress,
            RegulatoryBackground,
            AnalyzeRegulatoryBackgroundProgress,
            Checklist,
            AnalyzeChecklistProgress,
        ],
    )

    # await ProductProfile.create_index("product_code", unique=True)

    logger.info(
        "Database connection initialized successfully. Initializing email templates..."
    )
