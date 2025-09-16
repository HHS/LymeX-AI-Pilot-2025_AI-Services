from src.infrastructure.openai import get_openai_client
from src.services.openai.clear_uploaded_files import clear_uploaded_files


async def run() -> None:
    openai_client = get_openai_client()
    await clear_uploaded_files(openai_client)
