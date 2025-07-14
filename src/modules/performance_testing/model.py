from datetime import date, datetime, timezone
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
)


class PerformanceTesting(Document):
    """MongoDB persistence layer for the performance testing data."""

    product_id: str  # foreign‑key to ProductProfile document

    # Sub‑sections – optional so we can populate them lazily
    analytical: list[AnalyticalStudy] = Field(default_factory=list)
    comparison: list[ComparisonStudy] = Field(default_factory=list)
    clinical: list[ClinicalStudy] = Field(default_factory=list)
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
    missing_items: list[str] = Field(default_factory=list)

    created_at: date = Field(default_factory=date.today)
    updated_at: Optional[date] = None

    # Fast look‑up by product without strict ObjectId typing hassles
    product_id: str = Field(..., description="ID of the associated product", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

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
    """
    One document per product - tracks how many performance-testing
    sub-sections have been processed.
    """

    product_id: str = Field(..., index=True)

    total_sections: int  # how many sections we expect to run
    processed_sections: int = 0  # incremented after each section
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    class Settings:
        name = "performance_testing_analysis_progress"
