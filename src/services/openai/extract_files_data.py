from pathlib import Path
from typing import TypeVar
from fastapi import HTTPException
from pydantic import BaseModel
from loguru import logger
from src.environment import environment
from src.infrastructure.openai import get_openai_client
from src.services.openai.delete_files import delete_files
from src.services.openai.upload_files import upload_files


T = TypeVar("T", bound=BaseModel)


async def extract_files_data(
    file_paths: list[Path],
    system_instruction: str,
    user_question: str,
    model_class: type[T],
):
    openai_client = get_openai_client()
    logger.info("Extracting data from files: {}", file_paths)
    if not file_paths:
        logger.error("No file paths provided for extraction.")
        raise ValueError("No file paths provided for extraction.")
    uploaded_files = await upload_files(openai_client, file_paths)
    if not uploaded_files:
        logger.error("No files were uploaded successfully.")
        raise HTTPException(500, "No files were uploaded successfully.")
    logger.info("Files uploaded successfully: {}", [file.id for file in uploaded_files])
    logger.info("Creating OpenAI response with system instruction and user question.")
    logger.info(f"System instruction: {system_instruction}")
    logger.info(f"User question: {user_question}")
    try:
        response = await openai_client.responses.parse(
            model=environment.openai_model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": system_instruction,
                        },
                        {
                            "type": "input_text",
                            "text": """
Please ensure that all fields are included and that their types match the schema.
And the meaning should be the same as expressed in the comment of each field.
Only return data that available in the documents. Do not infer or assume any data that is not present in the documents.
Words like "unknown", "not available", "not applicable".. should be used if the data is not present in the documents.
""",
                        },
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": user_question,
                        },
                        *[
                            {
                                "type": "input_file",
                                "file_id": uploaded_file.id,
                            }
                            for uploaded_file in uploaded_files
                        ],
                    ],
                },
            ],
            text_format=model_class,
        )
        logger.info("OpenAI response received, processing output.")
        result = response.output_parsed
    finally:
        try:
            await delete_files(openai_client, [file.id for file in uploaded_files])
        except Exception as e:
            logger.error("Failed to delete files after extraction: {}", e)

    if not result:
        logger.error("No output parsed from the response.")
        raise HTTPException(500, "No output parsed from the response.")
    if isinstance(result, model_class):
        logger.info("Output matches the expected model class.")
    else:
        logger.error("Output does not match the expected model class.")
        raise HTTPException(500, "Output does not match the expected model class.")
    logger.info("Files deleted successfully after extraction.")
    return result
