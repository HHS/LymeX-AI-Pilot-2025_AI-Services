from loguru import logger
from src.infrastructure.redis import redis_client
from src.modules.clinical_trial.model import ClinicalTrial
from src.modules.clinical_trial.schema import ClinicalTrialStatus


async def analyze_clinical_trial(product_id) -> list[ClinicalTrial]:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeClinicalTrial:AnalyzeLock:{product_id}",
        timeout=5,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Lock already acquired for clinical trial {product_id}. Skipping analysis."
        )
        return
    clinical_trials: list[ClinicalTrial] = []
    clinical_trial = ClinicalTrial(
        product_id=product_id,
        name="Evaluation of Novel Cardiac Device in Heart Failure Patients",
        sponsor="Boston Scientific Corporation",
        study_design="Randomized Control",
        enrollment=2500,
        status=ClinicalTrialStatus.ACTIVE,
        phase=3,
        outcome="Reduction in major adverse cardiac events (MACE) over 24 months",
        inclusion_criteria=[
            "Adults aged 18-75 with chronic heart failure",
            "NYHA Class II-IV",
            "LVEF < 40%",
            "Informed consent provided",
        ],
        marked=False,
    )
    clinical_trials.append(clinical_trial)
    clinical_trial = ClinicalTrial(
        product_id=product_id,
        name="Long-Term Safety of New Anticoagulant in Atrial Fibrillation",
        sponsor="Bayer AG",
        study_design="Open Label Extension",
        enrollment=1500,
        status=ClinicalTrialStatus.RECRUITING,
        phase=4,
        outcome="Incidence of stroke and major bleeding events over 36 months",
        inclusion_criteria=[
            "Adults aged 40-85 with non-valvular atrial fibrillation",
            "CHA2DS2-VASc score ≥ 2",
            "Informed consent provided",
        ],
        marked=True,
    )
    clinical_trials.append(clinical_trial)
    await ClinicalTrial.find(ClinicalTrial.product_id == str(product_id)).delete_many()
    await ClinicalTrial.insert_many(clinical_trials)

    logger.info(f"Clinical trial analysis completed for product_id: {product_id}")
    await lock.release()
    logger.info(f"Released lock for clinical trial {product_id}.")
