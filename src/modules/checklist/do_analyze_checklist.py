from pathlib import Path
from loguru import logger
from src.modules.checklist.questions import questions
from src.modules.checklist.model import (
    Checklist,
)
from src.modules.checklist.schema import ChecklistSchema
from src.modules.performance_testing.storage import get_performance_testing_documents
from src.modules.product_profile.storage import get_product_profile_documents
from src.services.openai.extract_files_data import extract_files_data


system_instruction = (
    "You are an FDA expert. Use the uploaded PDF files to extract a complete "
    "product profile. Return **only** valid JSON that matches the "
    "Checklist schema exactly (no explanations or bullet points). "
    "If a field is not found, return the field value as None."
)
user_question = (
    "Please extract a complete information using all uploaded FDA PDF "
    "If an answer is not found, return the field value 'Not Available', do not make up an answer.\n\n"

    f"{questions}"
)


async def do_analyze_checklist(product_id: str) -> None:
    product_profile_documents = await get_product_profile_documents(product_id)
    performance_testing_documents = await get_performance_testing_documents(product_id)

    product_profile_document_paths: list[Path] = [
        Path(doc.path) for doc in product_profile_documents if doc.path
    ]
    performance_testing_document_paths: list[Path] = [
        Path(doc.path) for doc in performance_testing_documents if doc.path
    ]
    checklist_document_paths = [
        *product_profile_document_paths,
        *performance_testing_document_paths,
    ]

    result = await extract_files_data(
        file_paths=checklist_document_paths,
        system_instruction=system_instruction,
        user_question=user_question,
        model_class=ChecklistSchema,
    )

    # Save checklist
    await Checklist.find(Checklist.product_id == product_id).delete_many()
    record = {
        **result.model_dump(),
        "product_id": product_id,
    }
    await Checklist(**record).save()

    logger.info(f"Saved product checklist for {product_id}")
