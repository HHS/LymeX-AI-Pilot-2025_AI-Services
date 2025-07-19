from pathlib import Path
from openai import AsyncOpenAI
from openai.types import FilePurpose, FileObject


async def upload_file(
    openai_client: AsyncOpenAI,
    file_path: Path,
    purpose: FilePurpose = "user_data",
) -> FileObject:
    upload_file = await openai_client.files.create(
        file=file_path,
        purpose=purpose,
    )
    return upload_file




