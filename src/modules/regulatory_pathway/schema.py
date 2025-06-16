from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AlternativePathway(BaseModel):
    name: str
    confident_score: int


class RegulatoryPathwayJustification(BaseModel):
    title: str
    content: str

