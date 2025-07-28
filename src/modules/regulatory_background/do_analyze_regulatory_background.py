from pathlib import Path
from loguru import logger

from src.modules.regulatory_background.model import RegulatoryBackground
from src.modules.regulatory_background.schema import RegulatoryBackgroundSchema
from src.modules.regulatory_background.storage import (
    get_regulatory_background_documents,
)
from src.services.openai.extract_files_data import extract_files_data
from src.infrastructure.minio import get_object


system_instruction = """
You are an expert in FDA regulatory documentation for medical devices.

Your task:
- Read and analyze all uploaded FDA meeting minutes in PDF form.
- Extract and evaluate FDA's responses to the sponsor's questions.
- Identify whether the sponsor’s strategy aligns with FDA feedback.
- For each of the following categories:
  - Predicate device reference
  - Intended use
  - Clinical trial requirements
  - Risk classification
  - Regulatory submission history

Return a JSON object matching this structure:
- Each field should include:
  - title: A short summary of the topic
  - content: Extracted text from the FDA meeting minutes
  - suggestion: Any concerns, gaps, or follow-up actions suggested by FDA

Only include keys present in the schema. If a topic is not discussed, say "Not discussed in meeting" in all three fields.
"""

user_question = """
Analyze the uploaded FDA meeting minutes and produce a structured evaluation.
Return a JSON object matching the RegulatoryBackground schema.
"""

async def do_analyze_regulatory_background(product_id: str) -> None:
    regulatory_background_documents = await get_regulatory_background_documents(
        product_id
    )

    # Download each doc locally
    for doc in regulatory_background_documents:
        if not doc.path:
            continue
        local_path = Path(doc.path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(await get_object(doc.key))

    regulatory_background_document_paths: list[Path] = [
        Path(doc.path) for doc in regulatory_background_documents if doc.path
    ]

    result = await extract_files_data(
        file_paths=regulatory_background_document_paths,
        system_instruction=system_instruction,
        user_question=user_question,
        model_class=RegulatoryBackgroundSchema,
    )

    logger.debug(f"Extracted Regulatory Backgroung result: {result.model_dump_json(indent=2)}")

    # Save profile
    await RegulatoryBackground.find(
        RegulatoryBackground.product_id == product_id
    ).delete_many()
    record = {**result.model_dump(), "product_id": product_id}
    await RegulatoryBackground(**record).save()

    logger.info(f"Saved product profile for {product_id}")
