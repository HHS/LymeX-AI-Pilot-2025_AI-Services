from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TestInfo(BaseModel):
    name: str = Field(..., description="Name of the test")
    standard: str = Field(..., description="Standard of the test")
    status: str = Field(..., description="Status of the test")


class IdentifiedGapAndSuggestedAdjustment(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier for the identified gap and suggested adjustment",
    )
    name: str = Field(
        ..., description="Identified gap and suggested adjustment in the test"
    )
    description: str = Field(
        ..., description="Description of the identified gap and suggested adjustment"
    )
    accepted: bool | None = Field(
        None,
        description="Indicates if the identified gap and suggested adjustment is accepted, false is rejected, and null is not yet decided",
    )


class TestComparison(BaseModel):
    product_id: str
    comparison_name: str
    requirements: list[TestInfo]
    comparator: list[TestInfo]
    identified_gaps_and_suggested_adjustments: list[IdentifiedGapAndSuggestedAdjustment]
