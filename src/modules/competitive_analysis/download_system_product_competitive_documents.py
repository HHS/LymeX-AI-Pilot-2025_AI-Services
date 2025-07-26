from pathlib import Path

from loguru import logger
from pydantic import BaseModel
from src.infrastructure.minio import get_object
from src.infrastructure.qdrant import search_similar


system_data_folder = "system_data"


class SystemProductCompetitiveDocument(BaseModel):
    product_name: str
    product_competitive_document: Path
    confidence_score: float
    key: str  # S3 key for the document


async def download_system_product_competitive_documents(
    q_vector: list[float],
    number_of_documents: int,
) -> list[SystemProductCompetitiveDocument]:
    similar_docs = search_similar(
        q_vector,
        number_of_documents,
    )
    logger.info(
        f"Found similar competitor documents: {', '.join([doc.payload.get('product_name', 'Unknown') for doc in similar_docs])}"
    )
    system_competitor_documents: list[SystemProductCompetitiveDocument] = [
        SystemProductCompetitiveDocument(
            product_name=doc_.payload.get("product_name", "Unknown"),
            product_competitive_document=Path(
                f"/tmp/system_competitor_documents/{doc_.payload.get('filename', 'Unknown')}"
            ),
            confidence_score=doc_.score,
            key=f"{system_data_folder}/{doc_.payload.get('filename', 'Unknown')}",
        )
        for doc_ in similar_docs
    ]
    for doc in system_competitor_documents:
        logger.info(f"Downloading competitor document from MinIO with key={doc.key}")
        raw_data = await get_object(doc.key)
        doc.product_competitive_document.parent.mkdir(
            parents=True, exist_ok=True
        )
        doc.product_competitive_document.write_bytes(raw_data)
        logger.info(
            f"Saved competitor document to {doc.product_competitive_document}"
        )
    return system_competitor_documents
