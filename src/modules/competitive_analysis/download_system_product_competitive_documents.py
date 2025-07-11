from pathlib import Path

from loguru import logger
from src.infrastructure.minio import get_object
from src.infrastructure.qdrant import search_similar


system_data_folder = "system_data"


async def download_system_product_competitive_documents(
    product_summary: str, number_of_documents: int
) -> list[Path]:
    similar_docs = search_similar(
        product_summary,
        number_of_documents,
    )
    similar_docs_file_names = [
        doc.payload.get("filename", "Unknown") for doc in similar_docs
    ]
    similar_docs_file_names = [i for i in similar_docs_file_names if i != "Unknown"]
    logger.info(f"Found similar competitor documents: {similar_docs_file_names}")
    # download competitor documents
    system_competitor_documents = [
        Path(f"/tmp/system_competitor_documents/{name}") for name in similar_docs_file_names
    ]
    for doc in system_competitor_documents:
        key = f"{system_data_folder}/{doc.name}"
        logger.info(f"Downloading competitor document from MinIO with key={key}")
        raw_data = await get_object(key)
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_bytes(raw_data)
        logger.info(f"Saved competitor document to {doc}")
    return system_competitor_documents
