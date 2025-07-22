from loguru import logger

from src.infrastructure.redis import redis_client
from src.modules.regulatory_pathway.analyze_progress import AnalyzeProgress
from src.modules.regulatory_pathway.do_analyze_regulatory_pathway import (
    do_analyze_regulatory_pathway,
)


async def analyze_regulatory_pathway(product_id: str) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeRegulatoryPathway:AnalyzeLock:{product_id}",
        timeout=60,
    )
    if not await lock.acquire(blocking=False):
        logger.warning(f"Analysis already running for {product_id}")
        return

    try:
        progress = AnalyzeProgress()
        await progress.initialize(product_id, total_files=1)
        try:
            await do_analyze_regulatory_pathway(product_id)
        except Exception as exc:
            logger.error(f"Error analyzing {product_id}: {exc}")
            raise
        finally:
            await progress.complete()

    except Exception as exc:
        logger.error(f"Error analyzing {product_id}: {exc}")
        raise

    finally:
        try:
            await lock.release()
        except Exception:
            pass
