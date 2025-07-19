from pathlib import Path
from openai import AsyncOpenAI
from openai.types import FilePurpose, FileObject
from loguru import logger
from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent


async def upload_file(
    openai_client: AsyncOpenAI,
    file_path: Path,
    purpose: FilePurpose = "user_data",
) -> FileObject:
    logger.info(f"Uploading file: {file_path} with purpose: {purpose}")
    try:
        upload_file = await openai_client.files.create(
            file=file_path,
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
