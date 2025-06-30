from datetime import datetime
from enum import Enum                    
from typing import Optional, List        
from pydantic import BaseModel, Field


class ClassificationSource(str, Enum):
    FDA = "FDA"
    EU = "EU"
    OTHER = "OTHER"
    NOT_AVAILABLE = "not available"


class RegulatoryClassification(BaseModel):
    organization: str
    classification: str
    source: ClassificationSource = ClassificationSource.NOT_AVAILABLE
    product_code: Optional[str] = None          # FDA 3-letter code
    regulation_number: Optional[str] = None     # 21 CFR reference


class DeviceCharacteristics(BaseModel):
    device_description: str
    principle_of_operation: str
    interpretation_of_results: str
    #generic_name: Optional[str] = None
    storage_conditions: Optional[str] = None    # e.g. “2-8 °C”
    shelf_life: Optional[str] = None            # e.g. “18 months”
    sterility_status: Optional[str] = None      # Sterile / Non-sterile / N/A
    software_present: Optional[str] = None
    single_use_or_reprocessed_single_use_device: Optional[str] = None
    animal_derived_materials: Optional[str] = None


class PerformanceCharacteristics(BaseModel):
    analytical_sensitivity: str
    analytical_specificity: str
    precision_reproducibility: str
    clinical_performance: str
    performance_summary: str
    performance_references: list[str]


class Feature(BaseModel):
    name: str
    description: str
    icon: str | None = Field(None, description="Icon representing the feature")


class Performance(BaseModel):
    speed: int
    reliability: int


class ProductProfileDocumentResponse(BaseModel):
    document_name: str = Field(..., description="Title of the product profile document.")
    file_name: str = Field(..., description="File name of the document, including extension.")
    url: str = Field(..., description="Direct link to download or view the document.")
    uploaded_at: str = Field(..., description="Timestamp indicating when the document was uploaded.")
    author: str = Field(..., description="Name of the person or entity that authored the document.")
    size: int = Field(..., description="Document size in bytes.")

# Purely for OpenAI function calling (fields from YAML)
class ProductProfileFunctionSchema(BaseModel):
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
        default_factory=list,
        description="Step-by-step IFU extracted from labeling"
    )
