from pathlib import Path
import yaml
import os
from loguru import logger
from src.modules.product_profile.model import (
    ProductProfile,
)
from src.modules.product_profile.schema import ProductProfileSchema
from src.modules.product_profile.storage import get_product_profile_documents
from src.services.openai.extract_files_data import extract_files_data


def load_questionnaire_text():
    path = os.path.join("src", "resources", "device_description_questionnaire.yaml")
    with open(path, "r") as f:
        items = yaml.safe_load(f)
    return "\n".join(f"{item['id']}: {item['question']}" for item in items)


system_instruction = (
    "You are an FDA expert. Use the uploaded PDF files to extract a complete "
    "product profile. Return **only** valid JSON that matches the "
    "ProductProfile schema exactly (no explanations or bullet points). "
    "Required fields now include trade name, model number, generic name, "
    "FDA product code, CFR regulation number, storage conditions, shelf-life, "
    "sterility status, warnings, limitations, contraindications, and a "
    "step-by-step instructions-for-use list. Use the literal string "
    "'not available' for any field you cannot confidently extract."
)
user_question = (
    "Please extract a complete product profile using all uploaded FDA PDF "
    "document and return a JSON object matching the ProductProfile schema. "
    "Only include fields present in schema. In particular:\n"
    "• Determine the FDA regulatory pathway ('510(k)', 'De Novo', or 'Premarket Approval (PMA)').\n"
    "• Capture **trade name, model number, and generic name**.\n"
    "• Capture **FDA product code** and **21 CFR regulation number**.\n"
    "• Capture storage conditions, shelf-life, and sterility status if present.\n"
    "• List any warnings, limitations, or contraindications that appear in labeling.\n"
    "• Any software present, single-use or reprocessed single use device "
    "are there any animal-derived materials in the product \n"
    "• Provide a **step-by-step instructions-for-use** list.\n"
    "If an answer is not found, return the field value as 'not available'.\n\n"
    f"{load_questionnaire_text()}"
)


async def do_analyze_product_profile(product_id: str) -> None:
    product_profile_documents = await get_product_profile_documents(product_id)

    product_profile_document_paths: list[Path] = [
        Path(doc.path) for doc in product_profile_documents if doc.path
    ]

    result = await extract_files_data(
        file_paths=product_profile_document_paths,
        system_instruction=system_instruction,
        user_question=user_question,
        model_class=ProductProfileSchema,
    )

    # Save profile
    await ProductProfile.find(ProductProfile.product_id == product_id).delete_many()
    record = {**result.model_dump(), "product_id": product_id}
    await ProductProfile(**record).save()

    logger.info(f"Saved product profile for {product_id}")
