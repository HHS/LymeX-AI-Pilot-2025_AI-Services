from loguru import logger
from src.modules.competitive_analysis.analyze import RegulatoryPathway
from src.modules.regulatory_pathway.schema import (
    AlternativePathway,
    RegulatoryPathwayJustification,
)
from src.infrastructure.redis import redis_client


async def analyze_regulatory_pathway(product_id: str) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeRegulatoryPathway:AnalyzeLock:{product_id}",
        timeout=100,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Lock already acquired for test comparison {product_id}. Skipping analysis."
        )
        return
    regulatory_pathway = RegulatoryPathway(
        product_id=product_id,
        recommended_pathway="510(k)",
        confident_score=85,
        description="The product is classified under Class II and requires a 510(k) submission.",
        estimated_time_days=90,
        alternative_pathways=[
            AlternativePathway(
                name="De Novo Classification",
                confident_score=25,
            ),
            AlternativePathway(
                name="Premarket Approval (PMA)",
                confident_score=15,
            ),
        ],
        justifications=[
            RegulatoryPathwayJustification(
                title="Product Classification",
                content="Class II medical device with substantial equivalence to predicate devices",
            ),
            RegulatoryPathwayJustification(
                title="Risk Assessment",
                content="Low to moderate risk based on device characteristics and intended use",
            ),
        ],
        supporting_documents=[
            "https://example.com/supporting_document_1.pdf",
            "https://example.com/supporting_document_2.pdf",
        ],
    )
    await RegulatoryPathway.find(
        RegulatoryPathway.product_id == product_id,
    ).delete_many()
    await regulatory_pathway.save()

    logger.info(f"Regulatory pathway analysis completed for product_id: {product_id}")
    await lock.release()
    logger.info(f"Released lock for regulatory pathway {product_id}.")
