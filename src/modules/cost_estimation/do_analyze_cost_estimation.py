from pathlib import Path
from loguru import logger
from src.modules.regulatory_pathway.model import (
    RegulatoryPathway,
)
from src.modules.regulatory_pathway.schema import RegulatoryPathwaySchema
from src.modules.product_profile.storage import get_product_profile_documents
from src.services.openai.extract_files_data import extract_files_data


system_instruction = """
You are an expert at extracting structured information from regulatory and regulatory documentation for medical devices.

Your task:
- Read and analyze all uploaded PDF documents.
- Extract all relevant information and return a JSON object that exactly matches the following RegulatoryPathway schema.
- Only include fields present in the schema, matching their types and structure.
"""
user_question = """
Read all uploaded PDF documents and extract all relevant information. 
Return a JSON object matching the RegulatoryPathway schema (structure provided in your system instructions). 
Include as much detail as possible.
"""


async def do_analyze_regulatory_pathway(product_id: str) -> None:
    product_profile_documents = await get_product_profile_documents(product_id)

    product_profile_document_paths: list[Path] = [
        Path(doc.path) for doc in product_profile_documents if doc.path
    ]

    result = await extract_files_data(
        file_paths=product_profile_document_paths,
        system_instruction=system_instruction,
        user_question=user_question,
        model_class=RegulatoryPathwaySchema,
    )

    # Save pathway
    await RegulatoryPathway.find(
        RegulatoryPathway.product_id == product_id
    ).delete_many()
    record = {**result.model_dump(), "product_id": product_id}
    await RegulatoryPathway(**record).save()

    logger.info(f"Saved regulatory pathway for {product_id}")
