from pathlib import Path
from loguru import logger
from src.infrastructure.qdrant import embed_text
from src.modules.competitive_analysis.create_competitive_analysis import (
    create_competitive_analysis,
)
from src.modules.competitive_analysis.download_system_product_competitive_documents import (
    download_system_product_competitive_documents,
)
from src.modules.competitive_analysis.download_user_product_competitive_documents import (
    download_user_product_competitive_documents,
)
from src.modules.competitive_analysis.model import (
    CompetitiveAnalysis,
    CompetitiveAnalysisDetail,
)
from src.modules.index_system_data.summarize_files import summarize_files
from src.modules.product_profile.storage import get_product_profile_documents
from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent


async def do_analyze_competitive_analysis(product_id: str) -> None:
    logger.info(f"Starting competitive analysis for product_id={product_id}")

    product_profile_documents = await get_product_profile_documents(product_id)
    logger.debug(f"Fetched {len(product_profile_documents)} product profile documents for product_id={product_id}")

    product_profile_document_paths = [
        Path(doc.path) for doc in product_profile_documents if doc.path
    ]
    logger.debug(f"Product profile document paths: {product_profile_document_paths}")

    product_profile_summary = await summarize_files(product_profile_document_paths)
    logger.info(f"Product profile summary for {product_id}: {product_profile_summary}")

    q_vector = await embed_text(product_profile_summary.summary)
    logger.debug(f"Embedded product profile summary into vector for product_id={product_id}")

    system_competitor_documents = await download_system_product_competitive_documents(
        q_vector,
        2,
    )
    logger.info(f"Downloaded {len(system_competitor_documents)} system competitor documents for product_id={product_id}")

    user_competitor_documents = await download_user_product_competitive_documents(
        product_id,
        q_vector,
    )
    logger.info(f"Downloaded {len(user_competitor_documents)} user competitor documents for product_id={product_id}")

    user_docs_map = {doc.product_name: doc for doc in user_competitor_documents}
    to_remove_index: list[int] = []
    for i, sys_doc in enumerate(system_competitor_documents):
        user_doc = user_docs_map.get(sys_doc.product_name)
        if user_doc is not None:
            logger.debug(f"Merging system doc '{sys_doc.product_name}' into user competitor documents")
            user_doc.user_product_competitive_documents.append(
                sys_doc.system_product_competitive_document
            )
            to_remove_index.append(i)

    for i in reversed(to_remove_index):
        logger.debug(f"Removing merged system competitor document at index {i}")
        system_competitor_documents.pop(i)

    logger.info(
        f"After merging, {len(system_competitor_documents)} system competitor documents and "
        f"{len(user_competitor_documents)} user competitor documents remain for product_id={product_id}"
    )

    # --- SYSTEM COMPETITOR DOCS ---
    logger.info("Preparing self analysis task")
    self_tasks = [
        create_competitive_analysis(
            product_simple_name="Your Product",
            document_paths=product_profile_document_paths,
            confidence_score=1,
            use_system_data=False,
        )
    ]

    logger.info(f"Preparing {len(system_competitor_documents)} system competitor analysis tasks")
    system_tasks = [
        create_competitive_analysis(
            product_simple_name=comp_doc.product_name,
            document_paths=[comp_doc.system_product_competitive_document],
            confidence_score=comp_doc.confidence_score,
            use_system_data=True,
        )
        for comp_doc in system_competitor_documents
    ]

    # --- USER COMPETITOR DOCS ---
    logger.info(f"Preparing {len(user_competitor_documents)} user competitor analysis tasks")
    user_tasks = [
        create_competitive_analysis(
            product_simple_name=comp_doc.product_name,
            competitor_document_paths=comp_doc.user_product_competitive_documents,
            confidence_score=comp_doc.confidence_score,
            use_system_data=False,
        )
        for comp_doc in user_competitor_documents
    ]

    # --- RUN ALL TASKS IN PARALLEL ---
    logger.info("Running all competitive analysis tasks in parallel")
    competitive_analysis_details: list[
        CompetitiveAnalysisDetail
    ] = await async_gather_with_max_concurrent([
        *self_tasks,
        *system_tasks,
        *user_tasks,
    ])
    logger.info(f"Completed {len(competitive_analysis_details)} competitive analysis tasks")

    CompetitiveAnalysisDetail.insert_many(competitive_analysis_details)
    logger.info("Inserted competitive analysis details into database")

    competitive_analysis_list = [
        CompetitiveAnalysis(
            product_id=product_id,
            competitive_analysis_detail_id=doc.id,
            is_self_analysis=doc.product_simple_name == "Your Product",
        )
        for doc in competitive_analysis_details
    ]
    await CompetitiveAnalysis.insert_many(competitive_analysis_list)
    logger.info("Inserted competitive analysis records into database")

    logger.info(f"Competitive analysis for product_id={product_id} completed successfully")
