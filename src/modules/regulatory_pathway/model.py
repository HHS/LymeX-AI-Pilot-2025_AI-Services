from datetime import datetime
from beanie import Document, PydanticObjectId
from src.modules.regulatory_pathway.schema import (
    AlternativePathway,
    RegulatoryPathwayJustification,
)


class RegulatoryPathway(Document):
    product_id: str
    recommended_pathway: str
    confident_score: int
    description: str
    estimated_time_days: int
    alternative_pathways: list[AlternativePathway]
    justifications: list[RegulatoryPathwayJustification]
    supporting_documents: list[str]

    class Settings:
        name = "regulatory_pathway"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class AnalyzeRegulatoryPathwayProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_regulatory_pathway_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
