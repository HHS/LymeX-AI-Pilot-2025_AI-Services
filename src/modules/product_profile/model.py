from typing import Optional, List
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
    model_number: Optional[str] = None            
    reference_number: str
    description: str
    generic_name: Optional[str] = None            
    
    regulatory_pathway: Optional[str] = None      # now optional if absent
    regulatory_classifications: list[RegulatoryClassification]
    #product_code: Optional[str] = None            
    #regulation_number: Optional[str] = None       
    
    device_characteristics: list[DeviceCharacteristics]
    performance_characteristics: list[PerformanceCharacteristics]
    #features: list[Feature]
    claims: list[str]
    conflict_alerts: list[str]
    #test_principle: str
    comparative_claims: list[str]
    fda_approved: bool | None
    #ce_marked: bool | None

    #device_ifu_description: str
    instructions_for_use: list[str] = Field(default_factory=list)  

    #storage_conditions: Optional[str] = None     
    #shelf_life: Optional[str] = None             
    #sterility_status: Optional[str] = None       

    warnings: list[str] = Field(default_factory=list)              
    limitations: list[str] = Field(default_factory=list)           
    contraindications: list[str] = Field(default_factory=list)     

    #confidence_score: float
    sources: list[str]
    #performance: Performance
    price: int | None
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
