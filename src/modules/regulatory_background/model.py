from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.regulatory_background.schema import (
    RegulatoryBackgroundBase,
)


class RegulatoryBackground(Document, RegulatoryBackgroundBase):
    product_id: str

    class Settings:
        name = "regulatory_background"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class AnalyzeRegulatoryBackgroundProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_regulatory_background_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
