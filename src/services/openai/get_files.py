from openai import AsyncOpenAI
from openai.types import FileObject
from loguru import logger


async def get_files(openai_client: AsyncOpenAI) -> list[FileObject]:
    files = await openai_client.files.list()
    logger.info(f"Retrieved {len(files.data)} files.")
    return files.data
