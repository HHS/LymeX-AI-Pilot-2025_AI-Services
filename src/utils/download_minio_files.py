from src.infrastructure.minio import get_object
from pathlib import Path
from loguru import logger

from src.utils.async_gather_with_max_concurrent import async_gather_with_max_concurrent


async def download_minio_file(key: str) -> Path:
    logger.info(f"Downloading file from MinIO with key={key}")
    raw_data = await get_object(key)
    temp_path = Path(f"/tmp/{key}")
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(raw_data)
    logger.info(f"Saved file to {temp_path}")
    return temp_path


async def download_minio_files(keys: list[str]) -> list[Path]:
    keys = list(set(keys))

    tasks = [download_minio_file(key) for key in keys]
    downloaded_paths = await async_gather_with_max_concurrent(
        tasks,
    )
    logger.info(f"All files downloaded. Total files: {len(keys)}")
    logger.info(
        f"Downloaded files: {', '.join(str(path) for path in downloaded_paths)}"
    )
    return downloaded_paths
