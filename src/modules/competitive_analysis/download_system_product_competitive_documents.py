from pathlib import Path

from loguru import logger
from pydantic import BaseModel
from src.infrastructure.minio import get_object
from src.infrastructure.qdrant import search_similar
from src.modules.index_system_data.summarize_files import FileSummary


system_data_folder = "system_data"


class SystemProductCompetitiveDocument(BaseModel):
    product_name: str
    system_product_competitive_document: Path


async def download_system_product_competitive_documents(
    product_summary: FileSummary,
    number_of_documents: int,
) -> list[SystemProductCompetitiveDocument]:
    similar_docs = await search_similar(
        product_summary.summary,
        number_of_documents,
    )
    similar_docs = [doc.payload for doc in similar_docs if doc.payload]

    # similar_docs_file_names = [i for i in similar_docs_file_names if i != "Unknown"]
    logger.info(
        f"Found similar competitor documents: {', '.join([doc.get('product_name', 'Unknown') for doc in similar_docs])}"
    )
    # download competitor documents
    system_competitor_documents: list[SystemProductCompetitiveDocument] = [
        SystemProductCompetitiveDocument(
            product_name=doc_.get("product_name", "Unknown"),
            system_product_competitive_document=Path(
                f"/tmp/system_competitor_documents/{doc_.get('filename', 'Unknown')}"
            ),
        )
        for doc_ in similar_docs
    ]
    for doc in system_competitor_documents:
        key = f"{system_data_folder}/{doc.system_product_competitive_document.name}"
        logger.info(f"Downloading competitor document from MinIO with key={key}")
        raw_data = await get_object(key)
        doc.system_product_competitive_document.parent.mkdir(
            parents=True, exist_ok=True
        )
        doc.system_product_competitive_document.write_bytes(raw_data)
        logger.info(
            f"Saved competitor document to {doc.system_product_competitive_document}"
        )
    return system_competitor_documents
