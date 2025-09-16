from datetime import datetime
from beanie import Document, PydanticObjectId
from src.modules.regulatory_pathway.schema import RegulatoryPathwayBase


class RegulatoryPathway(Document, RegulatoryPathwayBase):
    product_id: str

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
