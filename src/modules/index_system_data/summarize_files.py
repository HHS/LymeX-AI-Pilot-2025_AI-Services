from pathlib import Path
from loguru import logger
from pydantic import BaseModel

from src.services.openai.extract_files_data import extract_files_data


class FileProductName(BaseModel):
    file_name: str
    product_name: str


class FileSummary(BaseModel):
    files: list[FileProductName]
    summary: str


async def summarize_files(paths: list[Path]) -> FileSummary:
    """
    Upload all PDFs in `paths` and use extract_files_data to get a summary and per-file product names.
    """
    if not paths:
        return FileSummary(files=[], summary="No documents to summarize.")

    # Define the system instruction and user question for the assistant
    system_instruction = (
        "You are an FDA subject-matter expert. For each attached PDF device form, "
        "extract the product name and file name. Then, provide:\n"
        "1. A list called 'files', with one object per file containing 'file_name' and 'product_name'.\n"
        "2. A field called 'summary', which is a concise 5-7 sentence summary focusing on the devices’ overall purpose and key features.\n"
        "Return your answer strictly as JSON matching the required schema."
    )

    user_question = (
        "Read all attached PDFs and respond with a JSON including: "
        "1) 'files' (list of file_name and extracted product_name per file), "
        "2) 'summary' (overall combined summary)."
    )

    # Call extract_files_data, which handles upload, query, cleanup, and schema validation
    result = await extract_files_data(
        file_paths=paths,
        system_instruction=system_instruction,
        user_question=user_question,
        model_class=FileSummary,
    )

    # Map extract result to your FileSummary domain model
    files = [
        FileProductName(file_name=f.file_name, product_name=f.product_name)
        for f in result.files
    ]
    summary = result.summary

    logger.info(f"Final summary for [{', '.join([p.name for p in paths])}]: {summary}")
    return FileSummary(files=files, summary=summary)
