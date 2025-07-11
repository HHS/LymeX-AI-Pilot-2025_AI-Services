from loguru import logger
from src.infrastructure.redis import redis_client
from src.modules.competitive_analysis.analyze_progress import AnalyzeProgress
from src.modules.competitive_analysis.create_competitive_analysis import (
    create_competitive_analysis,
)
from src.modules.competitive_analysis.download_system_product_competitive_documents import (
    download_system_product_competitive_documents,
)
from src.modules.competitive_analysis.get_and_download_product_profile_document import (
    get_and_download_product_profile_document,
)
from src.modules.competitive_analysis.download_user_product_competitive_documents import (
    download_user_product_competitive_documents,
)
from src.modules.competitive_analysis.model import (
    CompetitiveAnalysis,
)

NUMBER_OF_MANUAL_ANALYSIS = 3
TOTAL_ANALYSIS = 5


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

    docs, summary = await get_and_download_product_profile_document(product_id)

    # Initialize progress tracking
    progress = AnalyzeProgress()
    await progress.initialize(product_id, total_files=len(docs))

    logger.info(
        f"Searching for similar competitor documents for product_id={product_id}"
    )
    system_competitor_documents = await download_system_product_competitive_documents(
        summary,
        2,
    )
    user_competitor_documents = await download_user_product_competitive_documents(
        product_id
    )
    logger.info(
        f"Found {len(system_competitor_documents)} system competitor documents and "
        f"{len(user_competitor_documents)} user competitor documents for product_id={product_id}"
    )
    competitive_analysis_list: list[CompetitiveAnalysis] = []

    for comp_doc in system_competitor_documents:
        logger.info(
            f"Creating competitive analysis for competitor document {comp_doc.name}"
        )
        competitive_analysis = await create_competitive_analysis(
            product_profile_docs=docs, competitor_document_paths=[comp_doc]
        )
        competitive_analysis.reference_product_id = product_id
        competitive_analysis.use_system_data = True
        competitive_analysis_list.append(competitive_analysis)

    for comp_doc in user_competitor_documents:
        logger.info(
            f"Creating competitive analysis for user competitor document {comp_doc.product_name}"
        )
        competitive_analysis = await create_competitive_analysis(
            product_profile_docs=docs,
            competitor_document_paths=comp_doc.user_product_competitive_documents,
        )
        competitive_analysis.reference_product_id = product_id
        competitive_analysis.product_name = comp_doc.product_name
        competitive_analysis.use_system_data = False
        competitive_analysis_list.append(competitive_analysis)

    await CompetitiveAnalysis.find(
        CompetitiveAnalysis.reference_product_id == product_id,
    ).delete_many()
    await CompetitiveAnalysis.insert_many(competitive_analysis_list)
    await progress.complete()

    try:
        await lock.release()
        logger.info(f"Released lock for product {product_id}")
    except Exception as e:
        logger.error(f"Failed to release lock for product {product_id}: {e}")
