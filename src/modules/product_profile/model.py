from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field
from src.modules.product_profile.schema import (
    Feature,
    Performance,
    RegulatoryClassification,
)


class ProductProfile(Document):
    product_id: str
    reference_number: str
    description: str
    regulatory_pathway: str
    regulatory_classifications: list[RegulatoryClassification]
    device_description: str
    features: list[Feature]
    claims: list[str]
    conflict_alerts: list[str]
    fda_approved: bool | None
    ce_marked: bool | None
    device_ifu_description: str
    confidence_score: float
    sources: list[str]
    performance: Performance
    price: int | None
    instructions: list[str]
    type_of_use: str

    class Settings:
        name = "product_profile"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class AnalyzeProductProfileProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_product_profile_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
