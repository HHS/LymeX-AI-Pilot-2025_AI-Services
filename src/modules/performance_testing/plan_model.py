from datetime import datetime
from beanie import Document
from pydantic import Field

from src.modules.performance_testing.schema import PerformanceTestCard


class PerformanceTestPlan(Document):
    """Checklist of specific performance tests the device must provide."""

    product_id: str = Field(..., index=True)

    # required tests to be performed by user
    tests: list[PerformanceTestCard] = Field(default_factory=list)
    rejected_tests: list[PerformanceTestCard] = Field(default_factory=list)

    rationale: str | None = None  # optional narrative from the planner LLM

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Settings:
        name = "performance_test_plan"  # MongoDB collection name
        use_state_management = True
