from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from src.modules.clinical_trial.model import ClinicalTrial
from src.modules.performance_testing.model import PerformanceTesting
from src.modules.product.model import Product
from src.modules.regulatory_pathway.model import RegulatoryPathway
from src.modules.test_comparison.model import (
    TestComparison,
)
from src.modules.claim_builder.model import (
    AnalyzeClaimBuilderProgress,
    ClaimBuilder,
)
from src.modules.product_profile.model import (
    AnalyzeProductProfileProgress,
    ProductProfile,
)
from src.modules.competitive_analysis.model import (
    CompetitiveAnalysis,
    AnalyzeCompetitiveAnalysisProgress,
)
from src.environment import environment

client = AsyncIOMotorClient(environment.mongo_uri)
db = client[environment.mongo_db]


async def init_db() -> None:
    logger.info("Initializing database connection...")
    await init_beanie(
        database=db,
        document_models=[
            Product,
            CompetitiveAnalysis,
            AnalyzeCompetitiveAnalysisProgress,
            ProductProfile,
            AnalyzeProductProfileProgress,
            ClaimBuilder,
            AnalyzeClaimBuilderProgress,
            PerformanceTesting,
            TestComparison,
            ClinicalTrial,
            RegulatoryPathway,
        ],
    )
    logger.info(
        "Database connection initialized successfully. Initializing email templates..."
    )
