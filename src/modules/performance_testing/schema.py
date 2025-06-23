from enum import Enum
from pydantic import BaseModel, Field
import Optional

class PerformanceTestingStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"
    SUGGESTED = "Suggested"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class PerformanceTestingRiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PerformanceTestingConfidentLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PerformanceTestingReference(BaseModel):
    title: str = Field(..., description="Title of the reference")
    url: str = Field(..., description="URL of the reference")
    description: str = Field("", description="Description of the reference")


class AnalyticalPerformance(BaseModel):
    precision_repeatability: str = Field(..., description="Intra-run precision / repeatability")
    precision_reproducibility: str = Field(..., description="Inter-run precision / reproducibility")
    linearity: str = Field(..., description="Linearity range and correlation (r²)")
    analytical_sensitivity: str = Field(..., description="LoD / LoQ / analytical sensitivity")
    analytical_specificity: str = Field(..., description="Specificity / cross-reactivity")
    detection_limit: Optional[str] = Field(None, description="Detection limit if separate from LoD")
    measuring_range: Optional[str] = Field(None, description="Assay measuring range")
    cutoff: Optional[str] = Field(None, description="Cut-off study details")
    traceability: Optional[str] = Field(None, description="Traceability to reference material")
    stability: Optional[str] = Field(None, description="Stability / shelf-life summary")
    usability_human_factors: Optional[str] = Field(None, description="Usability / human-factors study summary")
    other_performance_data: Optional[str] = Field(None, description="Any other analytical data")

class ClinicalPerformance(BaseModel):
    clinical_sensitivity: str = Field(..., description="Clinical sensitivity from studies")
    clinical_specificity: str = Field(..., description="Clinical specificity from studies")
    clinical_cutoff: Optional[str] = Field(None, description="Clinical cut-off information")
    reference_range: Optional[str] = Field(None, description="Reference / expected values")
    pro_data: Optional[str] = Field(None, description="Patient-reported-outcomes data or refs (Q25)")
    ppi_data: Optional[str] = Field(None, description="Patient preference information data or refs (Q26)")
    other_clinical_data: Optional[str] = Field(None, description="Other supportive clinical data")


class ClinicalPerformance(BaseModel):
    clinical_sensitivity: str = Field(..., description="Clinical sensitivity")
    clinical_specificity: str = Field(..., description="Clinical specificity")
    clinical_cutoff: Optional[str] = Field(None, description="Clinical cut-off")
    reference_range: Optional[str] = Field(None, description="Reference / expected values")
    other_clinical_data: Optional[str] = Field(None, description="Other clinical data")


class PerformanceTestingFunctionSchema(BaseModel):
    analytical: AnalyticalPerformance
    clinical: ClinicalPerformance
    glp_protocol_compliance: Optional[str] = Field(
        None, description="Compliance statement for 21 CFR 58.120 (Q30)"
    )
    glp_report_compliance: Optional[str] = Field(
        None, description="Compliance statement for 21 CFR 58.185 (Q31)"
    )
    performance_summary: str
    performance_references: list[str]