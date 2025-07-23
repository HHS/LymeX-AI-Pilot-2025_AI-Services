import httpx, io
from loguru import logger


async def upload_via_url(client, url: str, filename: str) -> str:
    """Stream a PDF from MinIO (presigned URL) into OpenAI /files."""
    async with httpx.AsyncClient() as http:
        r = await http.get(url, timeout=60)
        r.raise_for_status()
    buf = io.BytesIO(r.content)
    buf.name = filename
    uploaded = client.files.create(file=buf, purpose="assistants")
    logger.debug("Uploaded {} → {}", filename, uploaded.id)
    return uploaded.id
