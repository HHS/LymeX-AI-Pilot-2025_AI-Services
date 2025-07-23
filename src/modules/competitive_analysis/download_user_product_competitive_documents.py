from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
from src.infrastructure.qdrant import embed_text
from src.modules.competitive_analysis.storage import get_competitive_analysis_documents
from src.modules.index_system_data.summarize_files import summarize_files
from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent


class Document(BaseModel):
    path: Path
    key: str  # S3 key


class UserProductCompetitiveDocument(BaseModel):
    product_name: str
    user_product_competitive_documents: list[Document]
    confidence_score: float


async def download_user_product_competitive_documents(
    product_id: str, q_vector: list[float]
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
        if competitor_name not in competitive_analysis_document_documents_dict:
            competitive_analysis_document_documents_dict[competitor_name] = []
        competitive_analysis_document_documents_dict[competitor_name].append(
            competitive_analysis_document_document
        )

    async def create_user_product_competitive_document(
        competitor_name: str,
        documents: list[Document],
    ) -> UserProductCompetitiveDocument:
        paths = [doc.path for doc in documents]
        user_upload_summary = await summarize_files(paths)
        user_upload_summary_vector = await embed_text(user_upload_summary.summary)
        confidence_score = cosine_similarity(user_upload_summary_vector, q_vector)
        return UserProductCompetitiveDocument(
            product_name=competitor_name,
            user_product_competitive_documents=documents,
            confidence_score=confidence_score,
        )

    result_tasks = [
        create_user_product_competitive_document(competitor_name, documents)
        for competitor_name, documents in competitive_analysis_document_documents_dict.items()
    ]
    user_product_competitive_documents = await async_gather_with_max_concurrent(
        result_tasks, max_concurrent=5
    )
    return user_product_competitive_documents
