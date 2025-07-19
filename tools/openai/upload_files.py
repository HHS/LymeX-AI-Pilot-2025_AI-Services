from pathlib import Path
from src.infrastructure.openai import get_openai_client
from src.services.openai.upload_files import upload_files


files = [
    Path("/Users/macbookpro/Downloads/K203292.pdf"),
    Path("/Users/macbookpro/Downloads/K220016.pdf"),
    Path("/Users/macbookpro/Downloads/K233367.pdf"),
    Path("/Users/macbookpro/Downloads/K240287.pdf"),
    Path("/Users/macbookpro/Downloads/K242767.pdf"),
]


async def run() -> None:
    openai_client = get_openai_client()
    await upload_files(openai_client, files)
