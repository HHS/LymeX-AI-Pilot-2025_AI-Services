from src.infrastructure.openai import get_openai_client
from src.services.openai.get_files import get_files


async def run() -> None:
    openai_client = get_openai_client()
    files = await get_files(openai_client)
    for file in files:
        print(
            f"File ID: {file.id}, File Name: {file.filename}, File Size: {file.bytes} bytes"
        )
        # You can add more processing logic here if needed
