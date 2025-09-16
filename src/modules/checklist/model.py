from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

from src.modules.checklist.schema import ChecklistBase


class Checklist(Document, ChecklistBase):
    product_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Settings:
        name = "checklist"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class AnalyzeChecklistProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_checklist_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
