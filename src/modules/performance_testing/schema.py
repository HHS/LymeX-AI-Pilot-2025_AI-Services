from __future__ import annotations

import enum
from datetime import date
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class RiskLevel(str, enum.Enum):
    """Overall risk assessment for a test or group of tests."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModuleStatus(str, enum.Enum):
    """Lifecycle state for the entire performance‑testing module."""

    PENDING = "pending"  # module created, nothing parsed yet
    IN_PROGRESS = "in_progress"  # AI extraction running / user filling gaps
    COMPLETED = "completed"  # all mandatory items satisfied
    NEEDS_REVIEW = "needs_review"  # AI finished but mandatory gaps remain

class PerformanceTestingSection(str, enum.Enum):
    """
    Canonical keys for each sub-section.  Keeping the names **exactly**
    in sync with the attribute names in PerformanceTestingDocument.
    """
    ANALYTICAL       = "analytical"
    COMPARISON       = "comparison"
    CLINICAL         = "clinical"
    ANIMAL_TESTING   = "animal_testing"
    EMC_SAFETY       = "emc_safety"
    WIRELESS         = "wireless"
    SOFTWARE         = "software"
    INTEROPERABILITY = "interoperability"
    BIOCOMPATIBILITY = "biocompatibility"
    STERILITY        = "sterility"
    SHELF_LIFE       = "shelf_life"
    CYBERSECURITY    = "cybersecurity"


class PerfTestingDocumentResponse(BaseModel):
    """
    Tiny DTO used by storage.py to return a single presigned URL.
    """
    url: str

class PerformanceTestingDocumentResponse(BaseModel):
    document_name: str = Field(
        ..., description="Name of the performance testing document"
    )
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    content_type: str = Field(
        ..., description="Content type of the document (e.g., PDF, DOCX)"
    )
    size: int = Field(..., description="Size of the document in bytes")



#------------------------------ Primitive nested objects – reused by multiple sub‑schemas ------------------------------

class AttachmentRef(BaseModel):
    """Reference to a file stored in the vector DB / S3 bucket etc."""

    id: str  # UUID or DB identifier
    description: Optional[str] = None  # e.g. "EMC Report – Annex B"


class PageRef(BaseModel):
    """Explicit page references for traceability."""

    page: int
    comment: Optional[str] = None


# Wireless‑specific helper
class WirelessFunction(BaseModel):
    name: str  # e.g. "BLE telemetry"
    risk_tier: Literal["a", "b", "c"]


# Interoperability‑specific helper
class ElectronicInterface(BaseModel):
    name: str  # e.g. "USB‑C"
    purpose: str  # e.g. "data & charging"
    status: Literal["active", "service", "inactive"]


# Biocompatibility‑specific helper
class BioMaterial(BaseModel):
    name: str  # e.g. "Medical grade silicone"
    tissue_type: Literal[
        "circulating_blood",
        "blood_path",
        "bone",
        "breast_milk",
        "dentin",
        "gas_mucosa",
        "communicating_mucosa",
        "contacting_skin",
    ]
    exposure_duration: Literal[
        "≤24h", ">24h ≤30d", ">30d"]


# Sterility‑specific helper
class SterilizationMethod(BaseModel):
    method_name: str  # e.g. "Ethylene Oxide"
    parameters_summary: Optional[str] = None  # temp, pressure, dwell time etc.


# ------------------------------ 1. Analytical studies ------------------------------

class AnalyticalStudy(BaseModel):
    study_type: Literal[
        "precision",
        "linearity",
        "sensitivity",
        "measuring_range",
        "cut_off",
        "traceability",
        "stability",
        "usability",
        "other",
    ]
    performed: bool = False
    attachments: List[AttachmentRef] = Field(default_factory=list)
    pages: List[PageRef] = Field(default_factory=list)
    confidence: Optional[float] = None  # 0‑1 from AI assessor
     # protocol metadata
    product_name:                Optional[str] = None
    product_identifier:          Optional[str] = None
    protocol_id:                 Optional[str] = None      # number & revision
    objective:                   Optional[str] = None
    specimen_description:        Optional[str] = None
    specimen_collection:         Optional[str] = None
    samples_replicates_sites:    Optional[str] = None
    positive_controls:           Optional[str] = None
    negative_controls:           Optional[str] = None
    calibration_requirements:    Optional[str] = None
    assay_steps:                 Optional[str] = None
    data_analysis_plan:          Optional[str] = None
    statistical_analysis_plan:   Optional[str] = None
    acceptance_criteria:         Optional[str] = None
    consensus_standards:         Optional[str] = None

    # report-specific additions
    deviations:                  Optional[str] = None
    discussion:                  Optional[str] = None
    conclusion:                  Optional[str] = None

    # free-form catch-all
    key_results:                 Optional[str] = None



# ------------------------------ 2. Comparison studies ------------------------------

class ComparisonStudy(BaseModel):
    study_type: Literal["method", "matrix"]
    performed: bool = False
    attachments: List[AttachmentRef] = Field(default_factory=list)
    comparator_device_k_number: Optional[str] = None
    summary: Optional[str] = None
    confidence: Optional[float] = None


# ------------------------------ 3. Clinical studies ------------------------------

class ClinicalStudy(BaseModel):
    sensitivity: Optional[float] = None  # 0‑1
    specificity: Optional[float] = None  # 0‑1
    clinical_cut_off: Optional[str] = None
    pro_included: Optional[bool] = None
    ppi_included: Optional[bool] = None
    attachments: List[AttachmentRef] = Field(default_factory=list)
    summary: Optional[str] = None
    confidence: Optional[float] = None


# ------------------------------ 4. Animal testing (GLP) ------------------------------

class AnimalTesting(BaseModel):
    glp_compliant: Optional[bool] = None
    justification_if_not_glp: Optional[str] = None
    attachments: List[AttachmentRef] = Field(default_factory=list)
    confidence: Optional[float] = None


# ------------------------------ 5. EMC / Electrical / Mechanical / Thermal safety ------------------------------

class EMCSafety(BaseModel):
    num_dut: Optional[int] = None  # number of devices tested
    worst_harm: Optional[Literal["death_serious", "non_serious", "no_harm"]] = None
    iec_edition: Optional[str] = None  # e.g. "IEC 60601‑1 Ed 3.2"
    asca: Optional[bool] = None  # FDA ASCA pilot used
    essential_performance: List[str] = Field(default_factory=list)  # EP functions
    pass_fail_pages: List[PageRef] = Field(default_factory=list)
    degradations_observed: Optional[str] = None
    allowances: Optional[str] = None
    deviations: Optional[str] = None
    final_version_tested: Optional[bool] = None
    attachments: List[AttachmentRef] = Field(default_factory=list)
    confidence: Optional[float] = None



# ------------------------------ 6. Wireless coexistence ------------------------------

class WirelessCoexistence(BaseModel):
    functions: List[WirelessFunction] = Field(default_factory=list)
    coexistence_tier_met: Optional[bool] = None
    fwp_summary: Optional[str] = None  # Functional Wireless Performance summary
    eut_exposed: Optional[bool] = None  # EUT exposed to expected signals
    fwp_maintained: Optional[bool] = None
    risk_mitigations_pages: List[PageRef] = Field(default_factory=list)
    attachments: List[AttachmentRef] = Field(default_factory=list)
    confidence: Optional[float] = None


# 7. ------------------------------ Software & cyber‑security performance ------------------------------

class SoftwarePerformance(BaseModel):
    contains_software: Optional[bool] = None
    digital_health: Optional[bool] = None  # SaMD / SiMD flag
    documentation_level: Optional[str] = None  # e.g. "moderate"
    architecture_views_present: Optional[bool] = None
    unresolved_anomalies_attachment: Optional[AttachmentRef] = None
    sbom_attachment: Optional[AttachmentRef] = None
    risk_assessment_attachment: Optional[AttachmentRef] = None
    patch_plan_pages: List[PageRef] = Field(default_factory=list)
    confidence: Optional[float] = None


# ------------------------------ 8. Interoperability ------------------------------

class Interoperability(BaseModel):
    interfaces: List[ElectronicInterface] | None = None
    risk_assessment_attachment: Optional[AttachmentRef] = None
    labeling_pages: List[PageRef] | None = None
    confidence: Optional[float] = None


# ------------------------------ 9. Biocompatibility ------------------------------

class Biocompatibility(BaseModel):
    tissue_contacting: Optional[bool] = None
    components: List[BioMaterial] | None = None
    repeat_exposure: Optional[bool] = None
    test_reports: List[AttachmentRef] | None = None
    rationale_if_no_test: Optional[str] = None
    confidence: Optional[float] = None


# ------------------------------ 10. Sterility validation ------------------------------

class SterilityValidation(BaseModel):
    packaged_as_sterile: Optional[bool] = None
    methods: Optional[List[SterilizationMethod]] = None  # making it optional
    sal: Optional[str] = None  # Sterility Assurance Level
    validation_method: Optional[str] = None  # half‑cycle, overkill etc.
    pyrogenicity_test: Optional[bool] = None
    packaging_description: Optional[str] = None
    modifications_warning_confirmed: Optional[bool] = None
    attachments: List[AttachmentRef] = Field(default_factory=list)
    confidence: Optional[float] = None


# ------------------------------ 11. Shelf‑life / accelerated aging ------------------------------

class ShelfLife(BaseModel):
    assessed_before: Optional[bool] = None
    proposed_shelf_life_months: Optional[int] = None
    attachments: List[AttachmentRef] = Field(default_factory=list)
    rationale_if_no_test: Optional[str] = None
    confidence: Optional[float] = None


# ------------------------------ 12. Cyber‑security (separate from SW performance as per questionnaire) ------------------------------

class CyberSecurity(BaseModel):
    threat_model_attachment: Optional[AttachmentRef] = None
    sbom_attachment: Optional[AttachmentRef] = None
    architecture_views_present: Optional[bool] = None
    risk_assessment_attachment: Optional[AttachmentRef] = None
    patch_plan_pages: List[PageRef] = Field(default_factory=list)
    eol_support_doc_attachment: Optional[AttachmentRef] = None
    security_controls_pages: List[PageRef] = Field(default_factory=list)
    confidence: Optional[float] = None


# ------------------------------ Aggregate document – what gets persisted in the DB ------------------------------

class PerformanceTesting(BaseModel):
    """Root document representing *all* performance‑testing evidence for a device."""

    id: str  # Beanie / Mongo primary key
    product_id: str  # foreign‑key to ProductProfile document

    # Sub‑sections – optional so we can populate them lazily
    analytical: List[AnalyticalStudy] = Field(default_factory=list)
    comparison: List[ComparisonStudy] = Field(default_factory=list)
    clinical: List[ClinicalStudy] = Field(default_factory=list)
    animal_testing: Optional[AnimalTesting] = None
    emc_safety: Optional[EMCSafety] = None
    wireless: Optional[WirelessCoexistence] = None
    software: Optional[SoftwarePerformance] = None
    interoperability: Optional[Interoperability] = None
    biocompatibility: Optional[Biocompatibility] = None
    sterility: Optional[SterilityValidation] = None
    shelf_life: Optional[ShelfLife] = None
    cybersecurity: Optional[CyberSecurity] = None

    # Roll‑up & meta
    overall_risk_level: Optional[RiskLevel] = None
    status: ModuleStatus = ModuleStatus.PENDING
    missing_items: List[str] = Field(default_factory=list)

    created_at: date = Field(default_factory=date.today)
    updated_at: Optional[date] = None


# Allow forward‑references (AnimalTesting etc.)
PerformanceTesting.update_forward_refs()

# ------------------------------ Export – used by other modules for type‑checking ------------------------------

__all__ = [
    "AttachmentRef",
    "PageRef",
    "AnalyticalStudy",
    "ComparisonStudy",
    "ClinicalStudy",
    "AnimalTesting",
    "EMCSafety",
    "WirelessCoexistence",
    "SoftwarePerformance",
    "Interoperability",
    "Biocompatibility",
    "SterilityValidation",
    "ShelfLife",
    "CyberSecurity",
    "PerformanceTesting",
    "RiskLevel",
    "ModuleStatus",
]
