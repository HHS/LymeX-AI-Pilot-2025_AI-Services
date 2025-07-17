from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId
from src.modules.product_profile.schema import (
    Feature,
    Performance,
    RegulatoryClassification,
    DeviceCharacteristics,
    PerformanceCharacteristics,
)


class ProductProfile(Document):
    product_id: str
    product_trade_name: str
    model_number: Optional[str]
    reference_number: str
    description: str
    generic_name: Optional[str]

    regulatory_pathway: Optional[str]
    regulatory_classifications: list[RegulatoryClassification]
    product_code: Optional[str]
    regulation_number: Optional[str]

    device_characteristics: list[DeviceCharacteristics]
    performance_characteristics: list[PerformanceCharacteristics]
    device_description: str
    features: list[Feature]
    claims: list[str]
    conflict_alerts: list[str]
    test_principle: str
    comparative_claims: list[str]
    fda_cleared: bool | None = None
    fda_approved: bool | None = None
    ce_marked: bool | None = None

    device_ifu_description: str
    instructions_for_use: list[str]

    storage_conditions: Optional[str]
    shelf_life: Optional[str]
    sterility_status: Optional[str]

    warnings: list[str]
    limitations: list[str]
    contraindications: list[str]

    confidence_score: float
    sources: list[str]
    performance: Performance
    price: int
    instructions: list[str]
    type_of_use: str

    # YAML-derived fields
    device_type: str
    disease_condition: str
    patient_population: str
    use_environment: str
    combination_use: str
    life_supporting: str
    specimen_type: str
    special_attributes: str

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
