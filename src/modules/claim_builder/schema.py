from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class IFUSource(BaseModel):
    source: str = Field(..., description="Source of the IFU phrase")
    reason: str = Field(..., description="Reason for including this phrase in the IFU")
    category: str = Field(
        ..., description="Category of the IFU phrase, e.g., safety, usage, maintenance"
    )  # Example: safety, usage, maintenance, etc.


class IFU(BaseModel):
    phrase: str = Field(
        ..., description="The phrase from the Instructions for Use (IFU)"
    )
    sources: list[IFUSource] | None = Field(
        None, description="List of sources for the IFU phrase"
    )


class ComplianceStatus(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Compliance(BaseModel):
    content: str
    status: ComplianceStatus


class MissingElementLevel(str, Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class MissingElement(BaseModel):
    id: int
    description: str
    suggested_fix: str
    level: MissingElementLevel
    accepted: bool | None = Field(
        None,
        description="Indicates if the missing element has been accepted. None if not decided yet.",
    )


class RiskIndicatorSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskIndicator(BaseModel):
    description: str
    severity: RiskIndicatorSeverity


class PhraseConflict(BaseModel):
    id: int = Field(..., description="ID of the phrase conflict, as index in the list")
    statement: str = Field(..., description="The statement causing the conflict")
    conflicting_regulation: str
    suggested_fix: str
    accepted_fix: str | None = Field(
        None,
        description="Accepted fix for the phrase conflict. None if not decided yet.",
    )
    rejected_reason: str | None = Field(
        None,
        description="Reason for rejecting the suggested fix. None if not rejected.",
    )


class Draft(BaseModel):
    version: int = Field(..., description="Version of the draft")
    updated_at: datetime = Field(
        ..., description="Date and time when the draft was last updated"
    )
    updated_by: str = Field(..., description="User email who last updated the draft")
    content: str = Field(..., description="Content of the draft claim builder")
    submitted: bool = Field(
        ..., description="Indicates if the draft has been submitted for review"
    )
    accepted: bool = Field(
        ..., description="Indicates if the draft has been accepted by the user"
    )
    reject_message: str | None = Field(
        None, description="Message provided by the user if the draft is rejected"
    )
