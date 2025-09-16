from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent
from openai import AsyncOpenAI
from loguru import logger


async def delete_file(
    openai_client: AsyncOpenAI,
    file_id: str,
) -> None:
    try:
        logger.info(f"[{file_id}] Deletion started.")
        await openai_client.files.delete(file_id=file_id)
        logger.info(f"[{file_id}] Deletion succeeded.")
    except Exception as e:
        logger.error(f"[{file_id}] Deletion failed: {e}", exc_info=True)


async def delete_files(
    openai_client: AsyncOpenAI,
    file_ids: list[str],
) -> None:
    """
    Deletes multiple files concurrently with a limit on simultaneous requests.
    Logs each attempt and provides a final summary.
    """
    logger.info(f"Initiating deletion of {len(file_ids)} files.")
    tasks = [delete_file(openai_client, file_id) for file_id in file_ids]
    await async_gather_with_max_concurrent(
        tasks,
    )

    logger.info("All delete requests completed.")
    logger.info(f"Total files processed: {len(file_ids)}")
