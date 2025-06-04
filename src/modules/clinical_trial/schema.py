from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ClinicalTrialStatus(str, Enum):
    PLANNED = "planned"
    RECRUITING = "recruiting"
    ACTIVE = "active"
    COMPLETED = "completed"


class ClinicalTrial(BaseModel):
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
