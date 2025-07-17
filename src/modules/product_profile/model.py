from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field
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
    model_number: Optional[str] = None
    reference_number: str = "Not Available"
    description: str = "Not Available"
    generic_name: Optional[str] = None

    regulatory_pathway: Optional[str] = None  # now optional if absent
    regulatory_classifications: list[RegulatoryClassification] = []
    product_code: Optional[str] = None
    regulation_number: Optional[str] = None

    device_characteristics: list[DeviceCharacteristics] = []
    performance_characteristics: list[PerformanceCharacteristics] = []
    device_description: str = "Not Available"
    features: list[Feature] = []
    claims: list[str] = []
    conflict_alerts: list[str] = []
    test_principle: str = "Not Available"
    comparative_claims: list[str] = []
    fda_cleared: bool | None = None
    fda_approved: bool | None = None
    ce_marked: bool | None = None

    device_ifu_description: str = 'Not available'
    instructions_for_use: list[str] = []

    storage_conditions: Optional[str] = None
    shelf_life: Optional[str] = None
    sterility_status: Optional[str] = None

    warnings: list[str] = []
    limitations: list[str] = []
    contraindications: list[str] = []

    confidence_score: float = 0.0
    sources: list[str] = []
    performance: Performance = None
    price: int = 0
    instructions: list[str] = []
    type_of_use: str = "Not Available"

    # YAML-derived fields
    device_type: str = "Not Available"
    disease_condition: str = "Not Available"
    patient_population: str = "Not Available"
    use_environment: str = "Not Available"
    combination_use: str = "Not Available"
    life_supporting: str = "Not Available"
    specimen_type: str = "Not Available"
    special_attributes: str = "Not Available"

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
