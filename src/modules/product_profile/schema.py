from enum import Enum
from typing import Optional, List
from pydantic import Field
from src.utils.base import SafeBase


class ClassificationSource(str, Enum):
    FDA = "FDA"
    EU = "EU"
    OTHER = "OTHER"
    NOT_AVAILABLE = "not available"


class RegulatoryClassification(SafeBase):
    organization: str = Field("Not Available", description="Organization name")
    classification: str = Field("Not Available", description="Classification")
    source: ClassificationSource = ClassificationSource.NOT_AVAILABLE
    product_code: Optional[str] = None
    regulation_number: Optional[str] = None


class DeviceCharacteristics(SafeBase):
    device_description: str = Field("Not Available", description="Device Description")
    principle_of_operation: str = Field(
        "Not Available", description="Principle of Operation"
    )
    interpretation_of_results: str = Field(
        "Not Available", description="Interpretation of Results"
    )
    # generic_name: Optional[str] = None
    storage_conditions: Optional[str] = None
    shelf_life: Optional[str] = None
    sterility_status: Optional[str] = None
    software_present: Optional[str] = None
    single_use_or_reprocessed_single_use_device: Optional[str] = None
    animal_derived_materials: Optional[str] = None


class PerformanceCharacteristics(SafeBase):
    analytical_sensitivity: str = Field(
        "Not Available", description="Analytical Senstivity"
    )
    analytical_specificity: str = Field(
        "Not Available", description="Analytical Specificity"
    )
    precision_reproducibility: str = Field(
        "Not Available", description="APrecision Reproducibility"
    )
    clinical_performance: str = Field(
        "Not Available", description="Clinical Performance"
    )
    performance_summary: str = Field(
        "Not Available", description="Overall Performance Summary"
    )
    performance_references: list[str] = Field(
        default_factory=list, description="Performance References"
    )


class Feature(SafeBase):
    name: str = Field("Not Available", description="Name")
    description: str = Field("Not Available", description="Description")
    icon: str | None = Field(None, description="Icon representing the feature")


class Performance(SafeBase):
    speed: int = Field(-1, description="Speed")
    reliability: int = Field(-1, description="Reliability")


class ProductProfileDocumentResponse(SafeBase):
    document_name: str = Field(..., description="Name of the product profile document")
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    size: int = Field(..., description="Size of the document in bytes")


# Purely for OpenAI function calling (fields from YAML)
class ProductProfileFunctionSchema(SafeBase):
    device_type: str
    disease_condition: str
    patient_population: str
    use_environment: str
    combination_use: str
    life_supporting: str
    specimen_type: str
    special_attributes: str

    product_trade_name: Optional[str] = None
    model_number: Optional[str] = None
    generic_name: Optional[str] = None

    warnings: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)

    instructions_for_use: List[str] = Field(
        default_factory=list, description="Step-by-step IFU extracted from labeling"
    )


class ProductProfileSchema(SafeBase):
    product_id: str = Field(..., description="Unique identifier for the product")
    product_trade_name: str = Field(
        "Not Available", description="Trade name of the product"
    )
    model_number: Optional[str] = Field(
        "Not Available", description="Model number of the product"
    )
    reference_number: str = Field(
        "Not Available", description="Reference number for the product"
    )
    description: str = Field("Not Available", description="Description of the product")
    generic_name: Optional[str] = Field(
        "Not Available", description="Generic name of the product"
    )

    regulatory_pathway: Optional[str] = Field(
        "Not Available", description="Regulatory pathway for product approval"
    )
    regulatory_classifications: list[RegulatoryClassification] = Field(
        default_factory=RegulatoryClassification,
        description="List of regulatory classifications",
    )
    product_code: Optional[str] = Field("Not Available", description="Product code")
    regulation_number: Optional[str] = Field(
        "Not Available", description="Regulation Number"
    )

    device_characteristics: list[DeviceCharacteristics] = Field(
        default_factory=DeviceCharacteristics,
        description="List of device characteristics",
    )
    performance_characteristics: list[PerformanceCharacteristics] = Field(
        default_factory=PerformanceCharacteristics,
        description="List of performance characteristics",
    )
    device_description: str = Field(
        "Not Available", description="Description of the device"
    )
    features: list[Feature] = Field(
        default_factory=Feature, description="List of device features"
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

    storage_conditions: Optional[str] = Field(
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
    use_environment: str = Field(
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
