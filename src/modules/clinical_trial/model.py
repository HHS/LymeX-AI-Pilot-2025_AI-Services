from beanie import Document, PydanticObjectId

from src.modules.clinical_trial.schema import ClinicalTrialStatus


class ClinicalTrial(Document):
    product_id: str
    name: str
    sponsor: str
    study_design: str
    enrollment: int
    status: ClinicalTrialStatus
    phase: int
    outcome: str
    inclusion_criteria: list[str]
    marked: bool = False

    class Settings:
        name = "clinical_trial"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
