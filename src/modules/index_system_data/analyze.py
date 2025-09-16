from loguru import logger
from src.infrastructure.qdrant import add_document, delete_document, get_all_documents
from src.modules.index_system_data.storage import (
    get_system_data_files,
    get_system_data_folder,
)
from src.modules.index_system_data.summarize_files import summarize_files
from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent
from src.utils.download_minio_files import download_minio_files


async def index_system_data() -> None:
    system_data_files = await get_system_data_files()
    indexed_system_data = get_all_documents()
    indexed_system_data_filenames = [
        doc["filename"] for doc in indexed_system_data if doc["filename"]
    ]
    logger.info(f"Indexed System Data: {indexed_system_data}")
    logger.info(f"System Data Files: {system_data_files}")
    files_to_index = [
        file for file in system_data_files if file not in indexed_system_data_filenames
    ]
    files_to_unindex = [
        file for file in indexed_system_data_filenames if file not in system_data_files
    ]
    logger.info(f"Files to Index: {files_to_index}")
    logger.info(f"Files to Unindex: {files_to_unindex}")

    system_data_folder = get_system_data_folder()
    files_to_index_keys = [f"{system_data_folder}/{file}" for file in files_to_index]
    files_to_index_paths = await download_minio_files(files_to_index_keys)
    files_to_index_summarize_tasks = [
        summarize_files([file_path]) for file_path in files_to_index_paths
    ]
    files_to_index_summaries = await async_gather_with_max_concurrent(
        files_to_index_summarize_tasks,
    )
    add_document_tasks = [
        add_document(file_path.name, summary)
        for file_path, summary in zip(files_to_index_paths, files_to_index_summaries)
    ]
    await async_gather_with_max_concurrent(add_document_tasks)

    # 4) remove deleted files from Qdrant
    for filename in files_to_unindex:
        delete_document(filename)
        logger.info(f"  • removed {filename}")
