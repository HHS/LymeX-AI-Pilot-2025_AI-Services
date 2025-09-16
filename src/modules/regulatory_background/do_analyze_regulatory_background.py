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
- Read and analyze all uploaded FDA regulatory background documents, including meeting minutes, feedback letters, submissions, and supporting material.
- Summarize the regulatory background in three sections: `summary`, `findings`, and `conflicts`.

**Output JSON structure:**

summary:
  title: Short summary title
  description: 2–4 sentence description of the product's regulatory background
  highlights: List of key highlights, each with:
    - title: Short label
    - detail: Description of the highlight

findings: List of items, each with:
  - status: "found" or "missing"
  - field: machine-readable field key (e.g., "predicateDevice", "riskClassification")
  - label: human-friendly label for the field
  - value: extracted statement from the documents
  - sourceFile: file name where the information was found (if any)
  - sourcePage: page number (if applicable)
  - tooltip: short helper text explaining why this is important
  - suggestion: recommended improvement or action (if applicable)
  - confidenceScore: number from 0-100 if applicable
  - userAction: true/false if user action is required

conflicts: List of items, each with:
  - field: machine-readable field key
  - phrase: exact phrase from the document
  - conflict: description of the conflict
  - source: file name where the conflict was found
  - suggestion: how to resolve the conflict
  - userAction: true/false if user action is required

If you cannot find information for a field, mark `status` as "missing" and provide an appropriate suggestion and tooltip.
Do not invent facts.
Return only valid JSON matching the schema exactly.
"""

user_question = """
Analyze the uploaded FDA regulatory background documents and produce a structured JSON
with `summary`, `findings`, and `conflicts` as described in the system instructions.
"""


async def do_analyze_regulatory_background(product_id: str) -> bool:
    regulatory_background_documents = await get_regulatory_background_documents(
        product_id
    )

    if not regulatory_background_documents:
        logger.warning(
            f"No regulatory background documents found for product {product_id}"
        )
        await RegulatoryBackground.find(
            RegulatoryBackground.product_id == product_id
        ).delete_many()
        return False

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

    logger.debug(
        f"Extracted Regulatory Backgroung result: {result.model_dump_json(indent=2)}"
    )

    # Save profile
    await RegulatoryBackground.find(
        RegulatoryBackground.product_id == product_id
    ).delete_many()
    record = {**result.model_dump(), "product_id": product_id}
    await RegulatoryBackground(**record).save()

    logger.info(f"Saved product profile for {product_id}")
    return True
