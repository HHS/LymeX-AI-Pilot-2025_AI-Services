from pathlib import Path

import httpx
from loguru import logger
from src.modules.index_system_data.summarize_files import summarize_files
from src.modules.product_profile.schema import ProductProfileDocumentResponse
from src.modules.product_profile.storage import get_product_profile_documents


async def get_and_download_product_profile_document(
    product_id: str,
) -> tuple[list[ProductProfileDocumentResponse], str]:
    docs = await get_product_profile_documents(product_id)
    doc_paths: list[Path] = []
    logger.info(
        f"Found {len(docs)} product profile documents for product_id={product_id}"
    )
    for doc in docs:
        logger.info(f"Downloading product profile document from {doc.url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(doc.url)
            temp_path = Path(f"/tmp/product_profile/{doc.file_name}")
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Saved product profile document to {temp_path}")
            doc_paths.append(temp_path)

    logger.info(f"Summarizing product profile documents for product_id={product_id}")
    for attempt in range(3):
        try:
            summary = await summarize_files(doc_paths)
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}/3 failed to summarize files: {e}")
            if attempt == 2:
                raise

    return docs, summary
