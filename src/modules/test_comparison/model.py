from beanie import Document, PydanticObjectId
from src.modules.test_comparison.schema import (
    IdentifiedGapAndSuggestedAdjustment,
    TestInfo,
)


class TestComparison(Document):
    product_id: str
    comparison_name: str
    requirements: list[TestInfo]
    comparator: list[TestInfo]
    identified_gaps_and_suggested_adjustments: list[IdentifiedGapAndSuggestedAdjustment]

    class Settings:
        name = "test_comparison"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
