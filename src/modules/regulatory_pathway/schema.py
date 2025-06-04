from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AlternativePathway(BaseModel):
    name: str
    confident_score: int


class RegulatoryPathwayJustification(BaseModel):
    title: str
    content: str


class RegulatoryPathway(BaseModel):
    product_id: str
    recommended_pathway: str
    confident_score: int
    description: str
    estimated_time_days: int
    alternative_pathways: list[AlternativePathway]
    justifications: list[RegulatoryPathwayJustification]
    supporting_documents: list[str]
