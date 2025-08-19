from random import choice
from src.infrastructure.redis import redis_client
from loguru import logger
from src.modules.test_comparison.model import TestComparison
from src.modules.test_comparison.schema import (
    IdentifiedGapAndSuggestedAdjustment,
    TestInfo,
)


async def analyze_test_comparison(product_id: str) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzeTestComparison:AnalyzeLock:{product_id}",
        timeout=5,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Lock already acquired for test comparison {product_id}. Skipping analysis."
        )
        return

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
                suggestion="Suggestion for improvement of Sterilization Method Difference",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=1,
                name="Review Sterilization Approach",
                description="Evaluate EO sterilization as an alternative to steam method",
                suggestion="Suggestion for improvement of Review Sterilization Approach",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=2,
                name="Performance Testing Gaps",
                description="Identify gaps in performance testing compared to competitors",
                suggestion="Suggestion for improvement of Performance Testing Gaps",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=3,
                name="Environmental Compliance Gaps",
                description="Address gaps in environmental compliance testing",
                suggestion="Suggestion for improvement of Environmental Compliance Gaps",
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
                suggestion="Suggestion for improvement of Sterilization Method Difference",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=1,
                name="Review Sterilization Approach",
                description="Evaluate EO sterilization as an alternative to steam method",
                suggestion="Suggestion for improvement of Review Sterilization Approach",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=2,
                name="Performance Testing Gaps",
                description="Identify gaps in performance testing compared to competitors",
                suggestion="Suggestion for improvement of Performance Testing Gaps",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=3,
                name="Environmental Compliance Gaps",
                description="Address gaps in environmental compliance testing",
                suggestion="Suggestion for improvement of Environmental Compliance Gaps",
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
                suggestion="Suggestion for improvement of Sterilization Method Difference",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=1,
                name="Review Sterilization Approach",
                description="Evaluate EO sterilization as an alternative to steam method",
                suggestion="Suggestion for improvement of Review Sterilization Approach",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=2,
                name="Performance Testing Gaps",
                description="Identify gaps in performance testing compared to competitors",
                suggestion="Suggestion for improvement of Performance Testing Gaps",
            ),
            IdentifiedGapAndSuggestedAdjustment(
                id=3,
                name="Environmental Compliance Gaps",
                description="Address gaps in environmental compliance testing",
                suggestion="Suggestion for improvement of Environmental Compliance Gaps",
            ),
        ],
    )
    await TestComparison.find(TestComparison.product_id == product_id).delete_many()
    await TestComparison.insert_many(
        [test_comparison_1, test_comparison_2, test_comparison_3]
    )

    logger.info(f"Test comparison analysis completed for product_id: {product_id}")
    await lock.release()
    logger.info(f"Released lock for test comparison {product_id}.")
