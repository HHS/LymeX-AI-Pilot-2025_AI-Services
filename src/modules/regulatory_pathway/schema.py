from pydantic import BaseModel, Field


class AlternativePathway(BaseModel):
    name: str
    confident_score: int


class RegulatoryPathwayJustification(BaseModel):
    title: str
    content: str


class RegulatoryPathwayBase:
    recommended_pathway: str = Field(..., description="Recommended regulatory pathway")
    confident_score: int = Field(
        ..., description="Confidence score for the recommendation"
    )
    description: str = Field(..., description="Description of the recommended pathway")
    estimated_time_days: int = Field(
        ..., description="Estimated time in days for the pathway"
    )
    alternative_pathways: list[AlternativePathway] = Field(
        ..., description="List of alternative regulatory pathways"
    )
    justifications: list[RegulatoryPathwayJustification] = Field(
        ..., description="List of justifications for the recommendation"
    )
    supporting_documents: list[str] = Field(
        ..., description="List of supporting document URLs or identifiers"
    )


class RegulatoryPathwaySchema(BaseModel, RegulatoryPathwayBase): ...
