from pathlib import Path
from loguru import logger
from pydantic import BaseModel
from src.infrastructure.qdrant import embed_text
from src.modules.competitive_analysis.storage import get_competitive_analysis_documents
from src.modules.index_system_data.summarize_files import summarize_files
from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class Document(BaseModel):
    path: Path
    key: str  # S3 key


class UserProductCompetitiveDocument(BaseModel):
    product_name: str
    product_competitive_documents: list[Document]
    confidence_score: float


async def download_user_product_competitive_documents(
    product_id: str,
    q_vector: list[float],
    to_simple_name_map: dict[str, str],
) -> list[UserProductCompetitiveDocument]:
    competitive_analysis_documents = await get_competitive_analysis_documents(
        product_id
    )
    competitive_analysis_document_documents_dict: dict[str, list[Document]] = {}
    for competitive_analysis_document in competitive_analysis_documents:
        competitive_analysis_document_document = Document(
            path=competitive_analysis_document.path,
            key=competitive_analysis_document.key,
        )
        competitor_name = competitive_analysis_document.competitor_name
        if competitor_name in to_simple_name_map:
            competitor_name = to_simple_name_map[competitor_name]
        if competitor_name not in competitive_analysis_document_documents_dict:
            competitive_analysis_document_documents_dict[competitor_name] = []
        competitive_analysis_document_documents_dict[competitor_name].append(
            competitive_analysis_document_document
        )
        logger.info(
            f"Added document for competitor {competitor_name}: {competitive_analysis_document_document}"
        )

    async def create_user_product_competitive_document(
        competitor_name: str,
        documents: list[Document],
    ) -> UserProductCompetitiveDocument:
        paths = [doc.path for doc in documents]
        user_upload_summary = await summarize_files(paths)
        user_upload_summary_vector = await embed_text(user_upload_summary.summary)
        # Ensure vectors are numpy arrays and 2D for sklearn
        vec1 = np.array(user_upload_summary_vector).reshape(1, -1)
        vec2 = np.array(q_vector).reshape(1, -1)
        confidence_score = float(cosine_similarity(vec1, vec2)[0][0])

        return UserProductCompetitiveDocument(
            product_name=competitor_name,
            product_competitive_documents=documents,
            confidence_score=confidence_score,
        )

    result_tasks = [
        create_user_product_competitive_document(competitor_name, documents)
        for competitor_name, documents in competitive_analysis_document_documents_dict.items()
    ]
    product_competitive_document = await async_gather_with_max_concurrent(
        result_tasks, max_concurrent=5
    )
    return product_competitive_document
