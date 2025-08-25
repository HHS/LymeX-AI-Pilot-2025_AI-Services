from __future__ import annotations

import enum
from datetime import date, datetime
from typing import List, Optional, Literal
from beanie import PydanticObjectId

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


class TestStatus(str, enum.Enum):
    """Test Status based on AI and User input"""

    SUGGESTED = "suggested"  # Test suggested by AI
    ACCEPTED = "accepted"  # Test Accepted by User
    REJECTED = "rejected"  # Test Rejected by User


class PerformanceTestingConfidentLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PerformanceTestingReference(BaseModel):
    title: str
    url: str | None = None
    description: str | None = None


class PerformanceTestingAssociatedStandard(BaseModel):
    name: str  # e.g. "ISO 10993‑4"
    standard_name: str | None = None  # long title
    version: str | None = None  # "2017/AMD1:2020"
    url: str | None = None
    description: str | None = None


class PerformanceTestCard(BaseModel):
    section_key: str  # "analytical", "clinical", …
    test_code: str
    test_description: str = "not available"
    status: TestStatus = TestStatus.SUGGESTED
    risk_level: RiskLevel = RiskLevel.MEDIUM
    ai_confident: int | None = None  # 0‑100 %
    confident_level: PerformanceTestingConfidentLevel | None = None
    ai_rationale: str | None = None
    references: list[PerformanceTestingReference] | None = None
    associated_standards: list[PerformanceTestingAssociatedStandard] | None = None
    rejected_justification: str | None = None

    # ─── metadata filled by backend ────────────────────────────
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    product_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "ai@crowdplat.com"


class PerformanceTestingSection(str, enum.Enum):
    """
    Canonical keys for each sub-section.  Keeping the names **exactly**
    in sync with the attribute names in PerformanceTestingDocument.
    """

    ANALYTICAL = "analytical"
    COMPARISON = "comparison"
    CLINICAL = "clinical"
    ANIMAL_TESTING = "animal_testing"
    EMC_SAFETY = "emc_safety"
    WIRELESS = "wireless"
    SOFTWARE = "software"
    INTEROPERABILITY = "interoperability"
    BIOCOMPATIBILITY = "biocompatibility"
    STERILITY = "sterility"
    SHELF_LIFE = "shelf_life"
    CYBERSECURITY = "cybersecurity"


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
    key: str = Field(..., description="Key of the document in the storage system")
    path: str = Field(..., description="Path to the document in the local machine")


# ------------------------------ Primitive nested objects – reused by multiple sub‑schemas ------------------------------


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
    description: str
    status: Literal["active", "service", "inactive"]


# Biocompatibility‑specific helper
class BioMaterial(BaseModel):
    name: str  # e.g. "Medical grade silicone"
    tissue_contacting_device_name:Optional[str] = None # Q89
    materials_used: Optional[str] = None # Q90
    color_additives: Optional[str] = None # Q91
    intended_contact:Optional[Literal["Direct", "Indirect", "Both"]] = None # Q92
    fda_biocompatibility_compliant: Optional[bool] = None # Q93
    repeated_exposure: Optional[bool] = None # Q94
    tissue_contact_type: Literal[   # Q95
        "circulating_blood",
        "blood_path",
        "bone",
        "breast_milk",
        "dentin",
        "gas_mucosa",
        "communicating_mucosa",
        "contacting_skin",
    ]
    exposure_duration: Literal["≤24h", ">24h ≤30d", ">30d"] # Q96


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
    attachments: List[AttachmentRef] = Field([])
    pages: List[PageRef] = Field([])
    confidence: Optional[float] = None  # 0‑1 from AI assessor
    # protocol metadata
    product_name: Optional[str] = None
    product_identifier: Optional[str] = None
    protocol_id: Optional[str] = None  # number & revision
    objective: Optional[str] = None
    specimen_description: Optional[str] = None
    specimen_collection: Optional[str] = None
    samples_replicates_sites: Optional[str] = None
    positive_controls: Optional[str] = None
    negative_controls: Optional[str] = None
    calibration_requirements: Optional[str] = None
    assay_steps: Optional[str] = None
    data_analysis_plan: Optional[str] = None
    statistical_analysis_plan: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    consensus_standards: Optional[str] = None

    # report-specific additions
    deviations: Optional[str] = None
    discussion: Optional[str] = None
    conclusion: Optional[str] = None

    # free-form catch-all
    key_results: Optional[str] = None


# ------------------------------ 2. Comparison studies ------------------------------


class ComparisonStudy(BaseModel):
    study_type: Literal["method", "matrix"] # Q18 and Q19
    performed: bool = False
    attachments: List[AttachmentRef] = Field([])
    comparator_device_k_number: Optional[str] = None # Q32
    summary: Optional[str] = None
    confidence: Optional[float] = None


# ------------------------------ 3. Clinical studies ------------------------------


class ClinicalStudy(BaseModel):
    sensitivity: Optional[float] = None  # 0‑1 # Q20
    specificity: Optional[float] = None  # 0‑1 # Q20
    clinical_cut_off: Optional[str] = None
    pro_included: Optional[bool] = None # Q24
    ppi_included: Optional[bool] = None # Q24
    investigation_location: Optional[Literal["US only", "Out of US only","Both US and Out of US"]] = None # Q28
    attachments: List[AttachmentRef] = Field([]) # Q25 Q26
    summary: Optional[str] = None
    confidence: Optional[float] = None


# ------------------------------ 4. Animal testing (GLP) ------------------------------


class AnimalTesting(BaseModel):
    glp_compliant: Optional[bool] = None # Q30
    justification_if_not_glp: Optional[str] = None # Q31
    attachments: List[AttachmentRef] = Field([])
    confidence: Optional[float] = None


# ------------------------------ 5. EMC / Electrical / Mechanical / Thermal safety ------------------------------


class EMCSafety(BaseModel):
    num_dut: Optional[int] = None  # number of devices tested # Q34
    worst_harm: Optional[Literal["death_serious", "non_serious", "no_harm"]] = None # Q35
    iec_edition: Optional[str] = None  # e.g. "IEC 60601‑1 Ed 3.2" # Q36
    asca: Optional[bool] = None  # FDA ASCA pilot used # Q36
    final_version_tested: Optional[bool] = None # Q37
    essential_performance: List[str] = Field([])  # EP functions # Q37
    pass_fail_pages: List[PageRef] = Field([]) # Q39
    degradations_observed: Optional[str] = None # Q42
    allowances: Optional[str] = None # Q43
    deviations: Optional[str] = None # Q344
    wireless_on_during_emc: bool | None = None   # Q40
    smart_batt_standalone_tested: bool | None = None  # Q41
    mr_safety_status: str | None = None          # Q71 ("MR Safe" | "MR Conditional" | "MR Unsafe" | "Not Evaluated")
    attachments: List[AttachmentRef] = Field([])
    confidence: Optional[float] = None


# ------------------------------ 6. Wireless coexistence ------------------------------
class WirelessRiskTier(str, enum.Enum):
    NEGLIGIBLE = "Negligible"          # Q49a
    MINOR = "Minor (Tier 3)"           # Q49b
    MODERATE = "Moderate (Tier 2)"     # Q49c
    MAJOR = "Major (Tier 1)"           # Q49d


class WirelessTechnology(str, enum.Enum):
    BLUETOOTH = "Bluetooth"            # Q51a
    WIFI = "Wifi"                      # Q51b
    ZIGBEE = "Zigbee"                  # Q51c
    RFID = "RFID"                      # Q51d
    CELLULAR = "Cellular"              # Q51e
    OTHER = "Other"                    # Q51f


class RFIDRange(str, enum.Enum):
    SHORT = "Short Range (<6 inches)"  # Q52a
    LONG = "Long Range"                # Q52b


class WirelessQoS(BaseModel):
    """
    Q50: Summarize Quality of Service aspects. Keep brief, evidence-backed text.
    All fields optional; fill whatever you can parse.
    """
    accessibility: Optional[str] = Field(
        default=None,
        description="Signal stability/priority (e.g., consistent signal, no dropout)."
    )
    latency: Optional[str] = Field(
        default=None,
        description="Latency characteristics (e.g., real-time, minimal delay)."
    )
    throughput: Optional[str] = Field(
        default=None,
        description="Bandwidth / data volume handling."
    )
    data_integrity: Optional[str] = Field(
        default=None,
        description="Packet errors, encryption/auth, availability, redundancy."
    )

class WirelessCoexistence(BaseModel):
    functions: List[WirelessFunction] = Field([]) # Q47
    risks: Optional[str] = Field(
        default=None,
        description="Risks due to failure/disruption/delay; include inherent complete-loss risk. (Q48)"
    )
    safeguards: Optional[str] = Field(
        default=None,
        description="Safeguards/redundancies built into the function. (Q48)"
    )
    risk_tier: Optional[WirelessRiskTier] = Field(
        default=None,
        description="Risk of the wireless function per AAMI TIR69. (Q49)"
    )
    qos: Optional[WirelessQoS] = Field(
        default=None,
        description="QoS summary (Q50)."
    )
    technologies: Optional[List[WirelessTechnology]] = Field(
        default=None,
        description="Technologies used by this function (Q51)."
    )
    rfid_range: Optional[RFIDRange] = Field(
        default=None,
        description="If RFID is used, intended operating range (Q52)."
    )
    cellular_coverage_mitigations: Optional[str] = Field(
        default=None,
        description="If Cellular is used, mitigations for poor/no coverage and subscription management (Q53)."
    )
    coexistence_tier_met: Optional[bool] = None # Q54
    fwp_summary: Optional[str] = None  # Functional Wireless Performance summary # Q55
    eut_exposed: Optional[bool] = None  # EUT exposed to expected signals
    fwp_maintained: Optional[bool] = None # Q58
    risk_mitigations_pages: List[PageRef] = Field([])
    attachments: List[AttachmentRef] = Field([])
    confidence: Optional[float] = None


# 7. ------------------------------ Software & cyber‑security performance ------------------------------


class SoftwarePerformance(BaseModel):
    contains_software: Optional[bool] = None # Q60
    digital_health: Optional[bool] = None  # SaMD / SiMD flag # Q61
    documentation_level: Optional[str] = None  # e.g. "moderate" # Q62
    confidence: Optional[float] = None


# ------------------------------ 8. Interoperability ------------------------------


class Interoperability(BaseModel):
    interfaces: List[ElectronicInterface] | None = None # Covers Q79 to Q84
    risk_assessment_attachment: Optional[AttachmentRef] = None # Q85
    labeling_pages: List[PageRef] | None = None
    confidence: Optional[float] = None


# ------------------------------ 9. Biocompatibility ------------------------------


class Biocompatibility(BaseModel):
    tissue_contacting: Optional[bool] = None # Q86
    components: List[BioMaterial] | None = None 
    repeat_exposure: Optional[bool] = None
    test_reports: List[AttachmentRef] | None = None
    rationale_if_no_test: Optional[str] = None
    confidence: Optional[float] = None


# ------------------------------ 10. Sterility validation ------------------------------


class SterilityValidation(BaseModel):
    packaged_as_sterile: Optional[bool] = None # Q98
    methods: Optional[List[SterilizationMethod]] = None  # making it optional # Q99 and Q101
    sterilized_componets: Optional[str] = None # Q100
    radiation_dose: Optional[str] = None # Q102
    validation_standards: Optional[str] = None # Q103
    sterilant_residuals: Optional[str] = None # Q104
    validation_method: Optional[str] = None  # half‑cycle, overkill etc. #Q105 and Q106
    sterility_assurance_level: Optional[str] = None  # Sterility Assurance Level Q107
    pyrogenicity_test: Optional[bool] = None # Q108
    packaging_description: Optional[str] = None # Q109
    modifications_warning_confirmed: Optional[bool] = None
    attachments: List[AttachmentRef] = Field([])
    confidence: Optional[float] = None


# ------------------------------ 11. Shelf‑life / accelerated aging ------------------------------


class ShelfLife(BaseModel):
    assessed_before: Optional[bool] = None # Q110
    proposed_shelf_life_months: Optional[int] = None # Q111
    attachments: List[AttachmentRef] = Field([])
    rationale_if_no_test: Optional[str] = None
    confidence: Optional[float] = None


# ------------------------------ 12. Cyber‑security (separate from SW performance as per questionnaire) ------------------------------


class CyberSecurity(BaseModel):
    threat_model_attachment: Optional[AttachmentRef] = None
    threat_methedology: Optional[str] = None # Q65
    architecture_views_present: Optional[bool] = None # Q66
    risk_assessment_attachment: Optional[AttachmentRef] = None # Q67
    uses_exploitability_instead_of_probability: Optional[bool] = Field(
        default=None,
        description="Q68: From risk matrix; True if exploitability replaces probability." # Q68
    )
    sbom_attachment: Optional[AttachmentRef] = None # Q69
    eol_support_doc_attachment: Optional[AttachmentRef] = None # Q70
    supported_operating_systems: Optional[str] = None # Q71
    unresolved_anomalies_attachment: Optional[AttachmentRef] = None # Q73
    patch_plan_pages: List[PageRef] = Field([])
    security_controls_categories: Optional[str] = None # Q75
    security_controls_pages: List[PageRef] = Field([])
    confidence: Optional[float] = None


# ------------------------------ Aggregate document – what gets persisted in the DB ------------------------------


class PerformanceTesting(BaseModel):
    """Root document representing *all* performance‑testing evidence for a device."""

    id: str  # Beanie / Mongo primary key
    product_id: str  # foreign‑key to ProductProfile document

    # Sub‑sections – optional so we can populate them lazily
    analytical: List[AnalyticalStudy] = Field([])
    comparison: List[ComparisonStudy] = Field([])
    clinical: List[ClinicalStudy] = Field([])
    animal_testing: Optional[AnimalTesting] = None
    emc_safety: Optional[EMCSafety] = None
    wireless: Optional[WirelessCoexistence] = None
    software: Optional[SoftwarePerformance] = None
    interoperability: Optional[Interoperability] = None
    biocompatibility: Optional[Biocompatibility] = None
    sterility: Optional[SterilityValidation] = None
    shelf_life: Optional[ShelfLife] = None
    cybersecurity: Optional[CyberSecurity] = None
    magnetic_resonance_safety: Optional[str] = None  # Sterility Assurance Level Q112
    literature_references_included: Optional[bool] = None # Q113

    # Roll‑up & meta
    overall_risk_level: Optional[RiskLevel] = None
    status: ModuleStatus = ModuleStatus.PENDING
    missing_items: List[str] = Field([])

    created_at: date = Field(default_factory=date.today)
    updated_at: Optional[date] = None

# === LLM Predicate Comparison (additive types) ===============================

class LLMPredicateRow(BaseModel):
    section_key: str                 # e.g. "analytical", "clinical", ...
    test_code: str | None = None     # e.g. "precision", "clin_sens"
    label: str                       
    your_value: str | None = None
    predicate_value: str | None = None

class LLMGapFinding(BaseModel):
    title: str
    subtitle: str
    suggested_fix: str
    severity: Literal["info", "minor", "major", "critical"]
    section_key: str
    test_code: str | None = None

class LLMPredicateComparisonResult(BaseModel):
    product_id: str
    competitor_id: str | None = None
    competitor_name: str | None = None
    rows: list[LLMPredicateRow] = Field(default_factory=list)
    gaps: list[LLMGapFinding] = Field(default_factory=list)
    model_used: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    "PerformanceTestingConfidentLevel",
    "PerformanceTestingReference",
    "PerformanceTestingAssociatedStandard",
    "PerformanceTestCard",
    "LLMPredicateRow",
    "LLMGapFinding",
    "LLMPredicateComparisonResult",
]
