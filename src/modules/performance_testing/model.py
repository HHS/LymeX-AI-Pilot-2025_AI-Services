from datetime import datetime
from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field
from typing import Optional

from src.modules.performance_testing.schema import PerformanceTesting


class PerformanceTestingDocument(Document, PerformanceTesting):
    """MongoDB persistence layer for the performance testing data."""

    # Fast look‑up by product without strict ObjectId typing hassles
    product_id: str = Field(..., description="ID of the associated product", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "performance_testing"  # Mongo collection name
        use_state_management = True   # Enables Beanie's dirty‑tracking

    async def save(self, *args, **kwargs):
        """Override to auto stamp `updated_at`."""
        self.updated_at = datetime.utcnow()
        return await super().save(*args, **kwargs)

class AnalyzePerformanceTestingProgress(Document):
    product_id: str = Field(index=True)
    total_files: int
    processed_files: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "analyze_performance_progress"
