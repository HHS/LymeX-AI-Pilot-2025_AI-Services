from loguru import logger
from src.infrastructure.redis import redis_client
from src.modules.clinical_trial.model import ClinicalTrial
from src.modules.clinical_trial.schema import ClinicalTrialStatus
from src.modules.clinical_trial.service import refresh_trials

async def analyze_clinical_trial(product_id: str, condition: str, sponsors: list[str]) -> list[ClinicalTrial]:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeClinicalTrial:AnalyzeLock:{product_id}",
        timeout=5,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(f"Lock already acquired for clinical trial {product_id}. Skipping analysis.")
        return []

    try:
        # Clear previous results for idempotency
        await ClinicalTrial.find(ClinicalTrial.product_id == str(product_id)).delete_many()

        inserted = await refresh_trials(product_id=str(product_id), condition=condition, sponsors=sponsors)
        logger.info(f"Clinical trial refresh completed for product_id={product_id}. Upserted={inserted}")

        # Return the saved rows for the UI
        return await ClinicalTrial.find(ClinicalTrial.product_id == str(product_id)).to_list()

    finally:
        await lock.release()
        logger.info(f"Released lock for clinical trial {product_id}.")
