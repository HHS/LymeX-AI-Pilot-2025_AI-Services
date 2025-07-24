from pathlib import Path
from loguru import logger

from src.modules.regulatory_background.model import RegulatoryBackground
from src.modules.regulatory_background.schema import RegulatoryBackgroundSchema
from src.modules.regulatory_background.storage import (
    get_regulatory_background_documents,
)
from src.services.openai.extract_files_data import extract_files_data


system_instruction = """
You are an expert at extracting structured information from regulatory and regulatory documentation for medical devices.

Your task:
- Read and analyze all uploaded PDF documents.
- Extract all relevant information and return a JSON object that exactly matches the following RegulatoryBackground schema.
- Only include fields present in the schema, matching their types and structure.
"""
user_question = """
Read all uploaded PDF documents and extract all relevant information. 
Return a JSON object matching the RegulatoryBackground schema (structure provided in your system instructions). 
Include as much detail as possible.
"""


async def do_analyze_regulatory_background(product_id: str) -> None:
    regulatory_background_documents = await get_regulatory_background_documents(
        product_id
    )

    regulatory_background_document_paths: list[Path] = [
        Path(doc.path) for doc in regulatory_background_documents if doc.path
    ]

    result = await extract_files_data(
        file_paths=regulatory_background_document_paths,
        system_instruction=system_instruction,
        user_question=user_question,
        model_class=RegulatoryBackgroundSchema,
    )

    # Save profile
    await RegulatoryBackground.find(
        RegulatoryBackground.product_id == product_id
    ).delete_many()
    record = {**result.model_dump(), "product_id": product_id}
    await RegulatoryBackground(**record).save()

    logger.info(f"Saved product profile for {product_id}")
