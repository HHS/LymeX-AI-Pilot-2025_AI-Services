from src.modules.clinical_trial.schema import ClinicalTrial, ClinicalTrialStatus


async def analyze_clinical_trial(product_id) -> list[ClinicalTrial]:
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
    return clinical_trials
