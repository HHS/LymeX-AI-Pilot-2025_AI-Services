from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ClinicalTrialStatus(str, Enum):
    PLANNED = "planned"
    RECRUITING = "recruiting"
    ACTIVE = "active"
    COMPLETED = "completed"

