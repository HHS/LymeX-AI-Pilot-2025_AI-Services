from loguru import logger

from src.infrastructure.redis import redis_client
from src.modules.regulatory_background.analyze_progress import AnalyzeProgress
from src.modules.regulatory_background.do_analyze_regulatory_background import (
    do_analyze_regulatory_background,
)


async def analyze_regulatory_background(product_id: str) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeRegulatoryBackground:AnalyzeLock:{product_id}",
        timeout=15,
    )
    if not await lock.acquire(blocking=False):
        logger.warning(f"Analysis already running for {product_id}")
        return

    try:
        progress = AnalyzeProgress()
        await progress.initialize(product_id, total_files=1)
        try:
            have_document = await do_analyze_regulatory_background(product_id)
            if have_document:
                await progress.complete()
            else:
                await progress.pending()
        except Exception as exc:
            logger.exception(f"Error analyzing {product_id}: {exc}")
            await progress.err()
            raise

    except Exception as exc:
        logger.exception(f"Error analyzing {product_id}: {exc}")
        raise

    finally:
        try:
            await lock.release()
        except Exception:
            pass
