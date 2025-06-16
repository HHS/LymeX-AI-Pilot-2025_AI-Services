from enum import Enum
from pydantic import BaseModel, Field


class PerformanceTestingStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"
    SUGGESTED = "Suggested"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class PerformanceTestingRiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PerformanceTestingConfidentLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PerformanceTestingReference(BaseModel):
    title: str = Field(..., description="Title of the reference")
    url: str = Field(..., description="URL of the reference")
    description: str = Field("", description="Description of the reference")


class PerformanceTestingAssociatedStandard(BaseModel):
    name: str = Field(..., description="Name of the associated standard + version")
    standard_name: str = Field(..., description="Name of the associated standard")
    version: str = Field(..., description="Version of the associated standard")
    url: str = Field(..., description="URL of the associated standard")
    description: str = Field("", description="Description of the associated standard")
