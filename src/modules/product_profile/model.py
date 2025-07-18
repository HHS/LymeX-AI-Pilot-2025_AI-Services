from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field
from src.utils.base import SafeBase
from src.modules.product_profile.schema import (
    Feature,
    Performance,
    RegulatoryClassification,
    DeviceCharacteristics,
    PerformanceCharacteristics,
)


class ProductProfile(SafeBase, Document):
    product_id: str = Field(..., description="Unique identifier for the product")
    product_trade_name: str = Field("Not Available", description="Trade name of the product")
    model_number: Optional[str] = Field("Not Available", description="Model number of the product")
    reference_number: str = Field("Not Available", description="Reference number for the product")
    description: str = Field("Not Available", description="Description of the product")
    generic_name: Optional[str] = Field("Not Available", description="Generic name of the product")

    regulatory_pathway: Optional[str] = Field("Not Available", description="Regulatory pathway for product approval")
    regulatory_classifications: list[RegulatoryClassification] = Field(
        default_factory=RegulatoryClassification, 
        description="List of regulatory classifications"
    )
    product_code: Optional[str] = Field("Not Available", description="Product code")
    regulation_number: Optional[str] = Field("Not Available", description="Regulation Number")

    device_characteristics: list[DeviceCharacteristics] = Field(
        default_factory=DeviceCharacteristics, 
        description="List of device characteristics"
    )
    performance_characteristics: list[PerformanceCharacteristics] = Field(
        default_factory=PerformanceCharacteristics, 
        description="List of performance characteristics"
    )
    device_description: str = Field(
        "Not Available", description="Description of the device"
    )
    features: list[Feature] = Field(
        default_factory=Feature, 
        description="List of device features"
    )
    claims: list[str] = Field(
        default_factory=list, description="Claims made about the product"
    )
    conflict_alerts: list[str] = Field(
        default_factory=list, description="Alerts for any conflicts"
    )
    test_principle: str = Field(
        "Not Available", description="Principle of the test performed by the device"
    )
    comparative_claims: list[str] = Field(
        default_factory=list, description="Comparative claims with other products"
    )
    fda_cleared: bool | None = Field(None, description="FDA clearance status")
    fda_approved: bool | None = Field(None, description="FDA approval status")
    ce_marked: bool | None = Field(None, description="CE marking status")

    device_ifu_description: str = Field(
        "Not available", description="Description of instructions for use"
    )
    instructions_for_use: list[str] = Field(
        default_factory=list, description="Step-by-step instructions for use"
    )

    storage_conditions: Optional[str]  = Field(
        None, description="Storage conditions for the product"
    )
    shelf_life: Optional[str] = Field(None, description="Shelf life of the product")
    sterility_status: Optional[str] = Field(
        None, description="Sterility status of the product"
    )

    warnings: list[str] = Field(
        default_factory=list, description="Warnings associated with the product"
    )
    limitations: list[str] = Field(
        default_factory=list, description="Limitations of the product"
    )
    contraindications: list[str] = Field(
        default_factory=list, description="Contraindications for product use"
    )

    confidence_score: float = Field(
        0.0, description="Confidence score for the product profile"
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Sources of information for the product profile",
    )
    performance: Performance = Field(
        default_factory=Performance,
        description="Performance metrics for the product",
    )
    price: Optional[int] = Field(0, description="Price of the product")
    instructions: list[str] = Field(
        default_factory=list, description="General instructions for the product"
    )
    type_of_use: str = Field("Not Available", description="Type of use for the product")

    # YAML-derived fields
    device_type: str = Field("Not Available", description="Type of device")
    disease_condition: str = Field(
        "Not Available", description="Disease or condition addressed by the product"
    )
    patient_population: str = Field(
        "Not Available", description="Patient population for the product"
    )
    use_environment: str  = Field(
        "Not Available", description="Environment where the product is used"
    )
    combination_use: str = Field(
        "Not Available", description="Combination use with other products"
    )
    life_supporting: str = Field(
        "Not Available", description="Whether the product is life supporting"
    )
    specimen_type: str = Field("Not Available", description="Type of specimen used")
    special_attributes: str = Field(
        "Not Available", description="Special attributes of the product"
    )

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
