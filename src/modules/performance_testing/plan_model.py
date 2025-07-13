from datetime import datetime
from typing import Dict, List
from beanie import Document
from pydantic import Field

class PerformanceTestPlan(Document):
    """Checklist of specific performance tests the device must provide."""

    product_id: str = Field(..., index=True)

    # section_key → list of canonical test codes (see const.TEST_CATALOGUE)
    required_tests: Dict[str, List[str]]

    rationale: str | None = None  # optional narrative from the planner LLM

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Settings:
        name = "performance_test_plan"       # MongoDB collection name
        use_state_management = True
