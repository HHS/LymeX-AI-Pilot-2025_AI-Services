from loguru import logger

from src.infrastructure.redis import redis_client
from src.modules.checklist.analyze_progress import AnalyzeProgress
from src.modules.checklist.do_analyze_checklist import (
    do_analyze_checklist,
)


async def analyze_checklist(product_id: str) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeChecklist:AnalyzeLock:{product_id}", timeout=60
    )
    if not await lock.acquire(blocking=False):
        logger.warning(f"Analysis already running for {product_id}")
        return

    try:
        progress = AnalyzeProgress()
        await progress.initialize(product_id, total_files=1)
        try:
            await do_analyze_checklist(product_id)
        except Exception as exc:
            logger.exception(f"Error analyzing {product_id}: {exc}")
            raise
        finally:
            await progress.complete()

    except Exception as exc:
        logger.exception(f"Error analyzing {product_id}: {exc}")
        await progress.err()
        raise

    finally:
        try:
            await lock.release()
        except Exception:
            pass
