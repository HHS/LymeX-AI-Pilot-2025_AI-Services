from openai import AsyncOpenAI
from loguru import logger
from src.services.openai.delete_files import delete_files
from src.services.openai.get_files import get_files


async def clear_uploaded_files(openai_client: AsyncOpenAI) -> None:
    files = await get_files(openai_client)

    if not files:
        logger.info("No uploaded files to clear.")
        return
    logger.info(f"Found {len(files)} uploaded files to clear.")

    await delete_files(openai_client, [file.id for file in files])
    logger.info("Cleared all uploaded files successfully.")
