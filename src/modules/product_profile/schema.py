from enum import Enum
from pydantic import BaseModel, Field


class ProductProfileDocumentResponse(BaseModel):
    document_name: str = Field(..., description="Name of the product profile document")
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    size: int = Field(..., description="Size of the document in bytes")
    key: str = Field(..., description="Key of the document in the storage system")
    path: str = Field(..., description="Path to the document in the local machine")


class ClassificationSource(str, Enum):
    FDA = "FDA"
    EU = "EU"
    OTHER = "OTHER"
    NOT_AVAILABLE = "not available"


class RegulatoryClassification(BaseModel):
    organization: str = Field("Not Available", description="Organization name")
    classification: str = Field("Not Available", description="Classification")
    source: ClassificationSource = ClassificationSource.NOT_AVAILABLE
    product_code: str = Field("Not Available", description="Product code")
    regulation_number: str = Field("Not Available", description="Regulation number")


class Feature(BaseModel):
    name: str = Field("Not Available", description="Name")
    description: str = Field("Not Available", description="Description")
    icon: str | None = Field(None, description="Icon representing the feature")


class ProductProfileSchemaBase:
    product_trade_name: str = Field(
        "Not Available", description="Trade name of the product"
    )
    model_number: str = Field(
        "Not Available", description="Model number of the product"
    )
    reference_number: str = Field(
        "Not Available", description="Reference number for the product"
    )
    description: str = Field("Not Available", description="Description of the product")
    generic_name: str = Field(
        "Not Available", description="Generic name of the product"
    )

    regulatory_pathway: str = Field(
        "Not Available", description="Regulatory pathway for product approval"
    )
    regulatory_classifications: list[RegulatoryClassification] = Field(
        [],
        description="List of regulatory classifications",
    )
    product_code: str = Field("Not Available", description="Product code")
    regulation_number: str = Field("Not Available", description="Regulation Number")
    analytical_sensitivity: str = Field(
        "Not Available", description="Analytical Sensitivity"
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
    performance_references: list[str] = Field([], description="Performance References")
    device_description: str = Field(
        "Not Available", description="Description of the device"
    )
    features: list[Feature] = Field([], description="List of device features")
    claims: list[str] = Field([], description="Claims made about the product")
    conflict_alerts: list[str] = Field([], description="Alerts for any conflicts")
    test_principle: str = Field(
        "Not Available", description="Principle of the test performed by the device"
    )
    comparative_claims: list[str] = Field(
        [], description="Comparative claims with other products"
    )
    fda_cleared: bool | None = Field(
        None, description="FDA clearance status (None if not applicable)"
    )
    fda_approved: bool | None = Field(
        None, description="FDA approval status (None if not applicable)"
    )
    ce_marked: bool | None = Field(
        None, description="CE marking status (None if not applicable)"
    )
    device_ifu_description: str = Field(
        "Not available", description="Description of instructions for use"
    )
    instructions_for_use: list[str] = Field(
        [], description="Step-by-step instructions for use"
    )
    principle_of_operation: str = Field(
        "Not Available", description="Principle of Operation"
    )
    interpretation_of_results: str = Field(
        "Not Available", description="Interpretation of Results"
    )
    generic_name: str = Field("Not Available", description="Generic Name")
    storage_conditions: str = Field("Not Available", description="Storage Conditions")
    shelf_life: str = Field("Not Available", description="Shelf Life")
    sterility_status: str = Field("Not Available", description="Sterility Status")
    software_present: str = Field("Not Available", description="Software Present")
    single_use_or_reprocessed_single_use_device: str = Field(
        "Not Available", description="Single Use or Reprocessed Single Use Device"
    )
    animal_derived_materials: str = Field(
        "Not Available", description="Animal Derived Materials"
    )
    warnings: list[str] = Field([], description="Warnings associated with the product")
    limitations: list[str] = Field([], description="Limitations of the product")
    contraindications: list[str] = Field(
        [], description="Contraindications for product use"
    )
    confidence_score: float = Field(
        0.0, description="Confidence score for the product profile"
    )
    sources: list[str] = Field(
        [],
        description="Sources of information for the product profile",
    )
    speed: int = Field(-1, description="Speed")
    reliability: int = Field(-1, description="Reliability")
    price: int = Field(0, description="Price of the product")
    instructions: list[str] = Field(
        [], description="General instructions for the product"
    )
    type_of_use: str = Field("Not Available", description="Type of use for the product")
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


class ProductProfileSchema(BaseModel, ProductProfileSchemaBase): ...
