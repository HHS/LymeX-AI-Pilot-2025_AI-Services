from pathlib import Path
from openai import AsyncOpenAI
from openai.types import FilePurpose, FileObject
from loguru import logger
from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent
from src.utils.supported_file_extensions import convert_supported_file_extension_to_pdf


async def upload_file(
    openai_client: AsyncOpenAI,
    file_path: Path,
    purpose: FilePurpose = "user_data",
) -> FileObject:
    converted_file_path = await convert_supported_file_extension_to_pdf(file_path)

    logger.info(f"Uploading file: {converted_file_path} with purpose: {purpose}")
    try:
        upload_file = await openai_client.files.create(
            file=converted_file_path,
            purpose=purpose,
        )
        logger.success(
            f"Successfully uploaded file: {file_path} (id: {upload_file.id})"
        )
        return upload_file
    except Exception as e:
        logger.error(f"Failed to upload file: {file_path}. Error: {e}")
        raise


async def upload_files(
    openai_client: AsyncOpenAI,
    file_paths: list[Path],
    purpose: FilePurpose = "user_data",
) -> list[FileObject]:
    logger.info(f"Starting upload of {len(file_paths)} files with purpose: {purpose}")
    upload_tasks = [
        upload_file(openai_client, file_path, purpose) for file_path in file_paths
    ]
    results = await async_gather_with_max_concurrent(upload_tasks)
    logger.info(f"Finished uploading files. {len(results)} files processed.")
    return results
