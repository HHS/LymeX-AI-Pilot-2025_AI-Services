from pathlib import Path
from beanie import PydanticObjectId
from loguru import logger
from src.environment import environment
from src.infrastructure.qdrant import embed_text
from src.modules.competitive_analysis.create_competitive_analysis import (
    create_competitive_analysis,
)
from src.modules.competitive_analysis.download_system_product_competitive_documents import (
    download_system_product_competitive_documents,
)
from src.modules.competitive_analysis.download_user_product_competitive_documents import (
    Document,
    download_user_product_competitive_documents,
)
from src.modules.competitive_analysis.model import (
    CompetitiveAnalysis,
    CompetitiveAnalysisDetail,
)
from src.modules.competitive_analysis.schema import CompetitiveAnalysisSource
from src.modules.index_system_data.summarize_files import summarize_files
from src.modules.product.model import Product
from src.modules.product_profile.storage import get_product_profile_documents
from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent
from beanie.operators import In


async def do_analyze_competitive_analysis(product_id: str) -> None:
    product = await Product.find_one(Product.id == PydanticObjectId(product_id))
    if not product:
        logger.warning(f"Product not found for product_id={product_id}")
        return
    logger.info(f"Starting competitive analysis for product_id={product_id}")

    product_profile_documents = await get_product_profile_documents(product_id)
    logger.info(
        f"Fetched {len(product_profile_documents)} product profile documents for product_id={product_id}"
    )

    product_profile_document_paths = [
        Path(doc.path) for doc in product_profile_documents if doc.path
    ]
    logger.info(f"Product profile document paths: {product_profile_document_paths}")

    product_profile_summary = await summarize_files(product_profile_document_paths)
    logger.info(f"Product profile summary for {product_id}: {product_profile_summary}")

    q_vector = await embed_text(product_profile_summary.summary)
    logger.info(
        f"Embedded product profile summary into vector for product_id={product_id}"
    )

    system_competitor_documents = await download_system_product_competitive_documents(
        product,
        q_vector,
        environment.competitive_analysis_number_of_system_search_documents,
    )
    logger.info(
        f"Downloaded {len(system_competitor_documents)} system competitor documents for product_id={product_id}"
    )
    logger.info(system_competitor_documents)

    exist_competitive_analysis = await CompetitiveAnalysis.find(
        CompetitiveAnalysis.product_id == product_id
    ).to_list()
    exist_competitive_analysis_ids = [
        PydanticObjectId(analysis.competitive_analysis_detail_id)
        for analysis in exist_competitive_analysis
    ]
    if exist_competitive_analysis_ids:
        exist_competitive_analysis_details = await CompetitiveAnalysisDetail.find(
            In(CompetitiveAnalysisDetail.id, exist_competitive_analysis_ids)
        ).to_list()
        logger.info(
            f"Found {len(exist_competitive_analysis_details)} existing competitive analysis details for product_id={product_id}"
        )
    else:
        exist_competitive_analysis_details = []

    exist_competitive_analysis_details = [
        i
        for i in exist_competitive_analysis_details
        if i.product_simple_name != "Your Product"
    ]

    to_simple_name_map = {
        doc.product_name: doc.product_simple_name
        for doc in exist_competitive_analysis_details
    }

    logger.info(f"Simple name map: {to_simple_name_map}")

    user_competitor_documents = await download_user_product_competitive_documents(
        product_id,
        q_vector,
        to_simple_name_map,
    )
    logger.info(
        f"Downloaded {len(user_competitor_documents)} user competitor documents for product_id={product_id}"
    )

    user_docs_map = {doc.product_name: doc for doc in user_competitor_documents}
    to_remove_index: list[int] = []
    for i, sys_doc in enumerate(system_competitor_documents):
        user_doc = user_docs_map.get(sys_doc.product_name)
        if user_doc is not None:
            logger.info(
                f"Merging system doc '{sys_doc.product_name}' into user competitor documents"
            )
            user_doc.product_competitive_documents.append(
                Document(path=sys_doc.product_competitive_document, key=sys_doc.key)
            )
            to_remove_index.append(i)

    for i in reversed(to_remove_index):
        logger.info(f"Removing merged system competitor document at index {i}")
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
            sources=[
                CompetitiveAnalysisSource(
                    name=doc.file_name,
                    key=doc.key,
                )
                for doc in product_profile_documents
                if doc.path
            ],
            data_type="self_analysis",
        )
    ]

    logger.info(
        f"Preparing {len(system_competitor_documents)} system competitor analysis tasks"
    )
    system_tasks = [
        create_competitive_analysis(
            product_simple_name=comp_doc.product_name,
            document_paths=[comp_doc.product_competitive_document],
            confidence_score=comp_doc.confidence_score,
            use_system_data=True,
            sources=[
                CompetitiveAnalysisSource(
                    name=comp_doc.product_competitive_document.name,
                    key=comp_doc.key,
                )
            ],
            data_type="system_competitor",
        )
        for comp_doc in system_competitor_documents
    ]

    # --- USER COMPETITOR DOCS ---
    logger.info(
        f"Preparing {len(user_competitor_documents)} user competitor analysis tasks"
    )
    logger.info(user_competitor_documents)
    user_tasks = [
        create_competitive_analysis(
            product_simple_name=comp_docs.product_name,
            document_paths=[
                comp_doc.path for comp_doc in comp_docs.product_competitive_documents
            ],
            confidence_score=comp_docs.confidence_score,
            use_system_data=False,
            sources=[
                CompetitiveAnalysisSource(
                    name=comp_doc.path.name,
                    key=comp_doc.key if hasattr(comp_doc, "key") else comp_docs.key,
                )
                for comp_doc in comp_docs.product_competitive_documents
            ],
            data_type="user_competitor",
        )
        for comp_docs in user_competitor_documents
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
    logger.info(
        f"Completed {len(competitive_analysis_details)} competitive analysis tasks"
    )

    decided_cas = await CompetitiveAnalysis.find(
        CompetitiveAnalysis.product_id == product_id,
    ).to_list()
    decided_cas = [doc for doc in decided_cas if doc.accepted is not None]
    decided_ca_detail_ids = [doc.competitive_analysis_detail_id for doc in decided_cas]
    decided_ca_detail_ids_map = {
        doc.competitive_analysis_detail_id: doc for doc in decided_cas
    }
    decided_cads = await CompetitiveAnalysisDetail.find(
        In(
            CompetitiveAnalysisDetail.id,
            [PydanticObjectId(i) for i in decided_ca_detail_ids],
        )
    ).to_list()
    decided_cads_map = {
        doc.product_name: decided_ca_detail_ids_map[str(doc.id)] for doc in decided_cads
    }

    competitive_analysis_list: list[CompetitiveAnalysis] = []
    for doc in competitive_analysis_details:
        ca = CompetitiveAnalysis(
            product_id=product_id,
            competitive_analysis_detail_id=str(doc.id),
            is_self_analysis=doc.data_type == "self_analysis",
        )
        if doc.product_name in decided_cads_map:
            ca.accepted = decided_cads_map[doc.product_name].accepted
            ca.accept_reject_reason = decided_cads_map[
                doc.product_name
            ].accept_reject_reason
            ca.accept_reject_by = decided_cads_map[doc.product_name].accept_reject_by
        competitive_analysis_list.append(ca)

    logger.info(
        f"Removing existing competitive analysis records for product_id={product_id}"
    )
    await CompetitiveAnalysis.find(
        CompetitiveAnalysis.product_id == product_id
    ).delete_many()

    await CompetitiveAnalysis.insert_many(competitive_analysis_list)
    logger.info("Inserted competitive analysis records into database")

    logger.info(
        f"Competitive analysis for product_id={product_id} completed successfully"
    )
