from datetime import datetime, timezone
from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional

from src.modules.performance_testing.schema import (
    AnalyticalStudy,
    AnimalTesting,
    Biocompatibility,
    ClinicalStudy,
    ComparisonStudy,
    CyberSecurity,
    EMCSafety,
    Interoperability,
    ModuleStatus,
    RiskLevel,
    ShelfLife,
    SoftwarePerformance,
    SterilityValidation,
    WirelessCoexistence,
    LLMPredicateRow, 
    LLMGapFinding,
)


class PerformanceTesting(Document):
    product_id: str
    analytical: list[AnalyticalStudy] = Field([])
    comparison: list[ComparisonStudy] = Field([])
    clinical: list[ClinicalStudy] = Field([])
    animal_testing: AnimalTesting | None = None
    emc_safety: EMCSafety | None = None
    wireless: WirelessCoexistence | None = None
    software: SoftwarePerformance | None = None
    interoperability: Interoperability | None = None
    biocompatibility: Biocompatibility | None = None
    sterility: SterilityValidation | None = None
    shelf_life: ShelfLife | None = None
    cybersecurity: CyberSecurity | None = None
    overall_risk_level: RiskLevel | None = None
    magnetic_resonance_safety: Optional[str] = None  # Sterility Assurance Level Q112
    literature_references_included: Optional[bool] = None # Q113
    status: ModuleStatus = ModuleStatus.PENDING
    missing_items: list[str] = Field([])
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Settings:
        name = "performance_testing"  # Mongo collection name
        use_state_management = True  # Enables Beanie's dirty‑tracking

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    async def save(self, *args, **kwargs):
        """Override to auto stamp `updated_at`."""
        self.updated_at = datetime.utcnow()
        return await super().save(*args, **kwargs)


class AnalyzePerformanceTestingProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_performance_testing_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

class PredicateLLMAnalysis(Document):
    product_id: str
    product_name: str
    competitor_id: str | None = None
    competitor_name: str | None = None
    rows: list[LLMPredicateRow] = Field(default_factory=list)
    gaps: list[LLMGapFinding] = Field(default_factory=list)
    model_used: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Settings:
        name = "predicate_llm_analysis"

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)