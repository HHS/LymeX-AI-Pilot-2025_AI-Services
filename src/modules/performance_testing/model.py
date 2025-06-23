from datetime import datetime
from beanie import Document, PydanticObjectId

from src.modules.performance_testing.schema import (
    PerformanceTestingConfidentLevel,
    PerformanceTestingStatus,
    PerformanceTestingRiskLevel,
    PerformanceTestingReference,
    PerformanceTestingAssociatedStandard,
    AnalyticalPerformance,
    ClinicalPerformance
)


class PerformanceTesting(Document):
    product_id: str
    test_name: str
    test_description: str
    # Detailed extracted data
    analytical: AnalyticalPerformance
    clinical: ClinicalPerformance
    glp_protocol_compliance: str | None = None
    glp_report_compliance: str | None = None
    performance_summary: str
    status: PerformanceTestingStatus
    risk_level: PerformanceTestingRiskLevel
    ai_confident: int | None = None
    confident_level: PerformanceTestingConfidentLevel | None = None
    ai_rationale: str | None = None
    references: list[PerformanceTestingReference] | None = None
    associated_standards: list[PerformanceTestingAssociatedStandard] | None = None
    rejected_justification: str | None = None
    created_at: datetime
    created_by: str

    class Settings:
        name = "performance_testing"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
