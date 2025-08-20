from beanie import Document, PydanticObjectId
from typing import List, Optional
from pydantic import Field
from src.modules.clinical_trial.schema import ClinicalTrialStatus

class ClinicalTrial(Document):
    product_id: str
    # persist the trial id + links + extra fields needed by the card UI
    nct_id: Optional[str] = None
    protocol_url: Optional[str] = None
    summary_url: Optional[str] = None

    name: str
    sponsor: str
    study_design: str
    enrollment: int
    status: ClinicalTrialStatus
    phase: Optional[str] = None
    outcome: str

    # array for the “Primary Outcomes” section
    primary_outcomes: List[str] = Field(default_factory=list)

    inclusion_criteria: List[str]
    marked: bool = False

    class Settings:
        name = "clinical_trial"
        indexes = ["product_id", "nct_id"]

    class Config:
        json_encoders = {PydanticObjectId: str}
