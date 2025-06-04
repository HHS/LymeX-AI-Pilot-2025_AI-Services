from random import choice
from src.modules.test_comparison.schema import (
    IdentifiedGapAndSuggestedAdjustment,
    TestComparison,
    TestInfo,
)


async def analyze_test_comparison(product_id: str) -> list[TestComparison]:
    test_comparison_1 = TestComparison(
        product_id=product_id,
        comparison_name="Competitor Device 1",
        requirements=[
            TestInfo(
                name="Performance Testing",
                standard="ISO 17025",
                status=choice(["Required", "Optional"]),
            ),
            TestInfo(
                name="Environmental Testing",
                standard="ISO 14001",
                status=choice(["Required", "Optional"]),
            ),
            TestInfo(
                name="Safety Testing",
                standard="ISO 45001",
                status=choice(["Required", "Optional"]),
            ),
        ],
        comparator=[
            TestInfo(
                name="Competitor A Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
            TestInfo(
                name="Competitor B Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
            TestInfo(
                name="Competitor C Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
        ],
        identified_gaps_and_suggested_adjustments=[
            IdentifiedGapAndSuggestedAdjustment(
                id=0,
                name="Sterilization Method Difference",
                description="Consider EO sterilization validation based on comparator success",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=1,
                name="Review Sterilization Approach",
                description="Evaluate EO sterilization as an alternative to steam method",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=2,
                name="Performance Testing Gaps",
                description="Identify gaps in performance testing compared to competitors",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=3,
                name="Environmental Compliance Gaps",
                description="Address gaps in environmental compliance testing",
            ),
        ],
    )
    test_comparison_2 = TestComparison(
        product_id=product_id,
        comparison_name="Competitor Device 2",
        requirements=[
            TestInfo(
                name="Performance Testing",
                standard="ISO 17025",
                status=choice(["Required", "Optional"]),
            ),
            TestInfo(
                name="Environmental Testing",
                standard="ISO 14001",
                status=choice(["Required", "Optional"]),
            ),
            TestInfo(
                name="Safety Testing",
                standard="ISO 45001",
                status=choice(["Required", "Optional"]),
            ),
        ],
        comparator=[
            TestInfo(
                name="Competitor A Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
            TestInfo(
                name="Competitor B Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
            TestInfo(
                name="Competitor C Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
        ],
        identified_gaps_and_suggested_adjustments=[
            IdentifiedGapAndSuggestedAdjustment(
                id=0,
                name="Sterilization Method Difference",
                description="Consider EO sterilization validation based on comparator success",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=1,
                name="Review Sterilization Approach",
                description="Evaluate EO sterilization as an alternative to steam method",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=2,
                name="Performance Testing Gaps",
                description="Identify gaps in performance testing compared to competitors",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=3,
                name="Environmental Compliance Gaps",
                description="Address gaps in environmental compliance testing",
            ),
        ],
    )
    test_comparison_3 = TestComparison(
        product_id=product_id,
        comparison_name="Competitor Device 3",
        requirements=[
            TestInfo(
                name="Performance Testing",
                standard="ISO 17025",
                status=choice(["Required", "Optional"]),
            ),
            TestInfo(
                name="Environmental Testing",
                standard="ISO 14001",
                status=choice(["Required", "Optional"]),
            ),
            TestInfo(
                name="Safety Testing",
                standard="ISO 45001",
                status=choice(["Required", "Optional"]),
            ),
        ],
        comparator=[
            TestInfo(
                name="Competitor A Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
            TestInfo(
                name="Competitor B Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
            TestInfo(
                name="Competitor C Performance",
                standard="ISO 17025",
                status=choice(["Completed", "Gap Identified"]),
            ),
        ],
        identified_gaps_and_suggested_adjustments=[
            IdentifiedGapAndSuggestedAdjustment(
                id=0,
                name="Sterilization Method Difference",
                description="Consider EO sterilization validation based on comparator success",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=1,
                name="Review Sterilization Approach",
                description="Evaluate EO sterilization as an alternative to steam method",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=2,
                name="Performance Testing Gaps",
                description="Identify gaps in performance testing compared to competitors",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=3,
                name="Environmental Compliance Gaps",
                description="Address gaps in environmental compliance testing",
            ),
        ],
    )
    return [test_comparison_1, test_comparison_2, test_comparison_3]
