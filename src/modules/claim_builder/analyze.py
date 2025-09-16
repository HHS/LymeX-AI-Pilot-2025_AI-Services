"""
End-to-end analysis entry-point.
"""

from __future__ import annotations

from loguru import logger

from src.infrastructure.redis import redis_client
from src.modules.claim_builder.do_analyze_claim_builder import do_analyze_claim_builder
from .analyze_progress import AnalyzeProgress



async def analyze_claim_builder(product_id: str) -> None:
    """
    Background task entry that:
      • grabs IFU text,
      • gathers supporting PDFs,
      • calls OpenAI once (JSON-mode),
      • saves/overwrites the ClaimBuilder document.
    """

    lock_key = f"NOIS2:Background:AnalyzeClaimBuilder:AnalyzeLock:{product_id}"
    lock = redis_client.lock(lock_key, timeout=15)

    # --------------------------------- progress doc --------------------------------- #

    if not await lock.acquire(blocking=False):
        logger.info("[%s] another job in progress – skipping", product_id)
        return

    try:
        progress = AnalyzeProgress()
        await progress.init(product_id=product_id, total_files=1)
        try:
            await do_analyze_claim_builder(product_id)
        except Exception as exc:
            logger.exception(f"Error analyzing {product_id}: {exc}")
            raise
        finally:
            await progress.complete()

    except Exception as exc:
        logger.error("ClaimBuilder analysis failed for %s: %s", product_id, exc)
        await progress.err()
        raise
    finally:
        try:
            await lock.release()
        except Exception:
            pass
