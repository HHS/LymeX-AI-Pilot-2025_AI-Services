from random import randint
from loguru import logger
from src.infrastructure.redis import redis_client
from src.modules.performance_testing.model import PerformanceTesting
from src.modules.performance_testing.schema import (
    PerformanceTestingAssociatedStandard,
    PerformanceTestingConfidentLevel,
    PerformanceTestingReference,
    PerformanceTestingStatus,
)


async def analyze_performance_testing(
    performance_testing_id: str,
) -> None:
    lock = redis_client.lock(
        f"NOIS2:Background:AnalyzePerformanceTesting:AnalyzeLock:{performance_testing_id}",
        timeout=100,
    )
    lock_acquired = await lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            f"Lock already acquired for performance testing {performance_testing_id}. Skipping analysis."
        )
        return
    performance_testing = await PerformanceTesting.get(performance_testing_id)
    if not performance_testing:
        logger.error(f"Performance testing with ID {performance_testing_id} not found.")
        await lock.release()
        return
    performance_testing.status = PerformanceTestingStatus.IN_PROGRESS
    await performance_testing.save()
    logger.info(
        f"Started analyzing performance testing with ID {performance_testing_id}."
    )
    ai_confident = randint(50, 100)
    if ai_confident < 70:
        confident_level = PerformanceTestingConfidentLevel.LOW
    elif ai_confident < 90:
        confident_level = PerformanceTestingConfidentLevel.MEDIUM
    else:
        confident_level = PerformanceTestingConfidentLevel.HIGH
    performance_testing.ai_confident = ai_confident
    performance_testing.confident_level = confident_level
    performance_testing.ai_rationale = "The hemolysis performance test is recommended to ensure the device does not induce significant red blood cell destruction during use. This aligns with ISO 10993-4 and FDA guidance on blood-contacting devices, supporting safety claims and regulatory submission."
    performance_testing.references = [
        PerformanceTestingReference(
            title="FDA Guidance on Blood-Contacting Devices",
            url="https://www.fda.gov/files/vaccines%2C%20blood%20%26%20biologics/published/Guidance-for-Industry--Use-of-Sterile-Connecting-Devices-in-Blood-Bank-Practices.pdf",
            description="This guidance provides recommendations for the evaluation of blood-contacting devices, including performance testing requirements.",
        ),
        PerformanceTestingReference(
            title="ISO 10993-4: Biological evaluation of medical devices - Part 4: Selection of tests for interactions with blood",
            url="https://www.iso.org/standard/68936.html",
            description="This standard outlines the requirements for testing the interaction of medical devices with blood, including hemolysis testing.",
        ),
        PerformanceTestingReference(
            title="ISO 10993-1: Biological evaluation of medical devices - Part 1: Evaluation and testing within a risk management process",
            url="https://www.iso.org/standard/68936.html",
            description="This standard provides a framework for the biological evaluation of medical devices, including risk assessment and testing strategies.",
        ),
    ]
    performance_testing.associated_standards = [
        PerformanceTestingAssociatedStandard(
            name="ISO 10993-4",
            standard_name="Biological evaluation of medical devices - Part 4: Selection of tests for interactions with blood",
            version="2017",
            url="https://www.iso.org/standard/68936.html",
            description="This standard outlines the requirements for testing the interaction of medical devices with blood, including hemolysis testing.",
        ),
        PerformanceTestingAssociatedStandard(
            name="ISO 10993-1",
            standard_name="Biological evaluation of medical devices - Part 1: Evaluation and testing within a risk management process",
            version="2018",
            url="https://www.iso.org/standard/68936.html",
            description="This standard provides a framework for the biological evaluation of medical devices, including risk assessment and testing strategies.",
        ),
        PerformanceTestingAssociatedStandard(
            name="FDA Guidance on Blood-Contacting Devices",
            standard_name="Guidance for Industry - Use of Sterile Connecting Devices in Blood Bank Practices",
            version="2020",
            url="https://www.fda.gov/files/vaccines%2C%20blood%20%26%20biologics/published/Guidance-for-Industry--Use-of-Sterile-Connecting-Devices-in-Blood-Bank-Practices.pdf",
            description="This guidance provides recommendations for the evaluation of blood-contacting devices, including performance testing requirements.",
        ),
    ]
    performance_testing.status = PerformanceTestingStatus.SUGGESTED
    await performance_testing.save()
    logger.info(
        f"Completed analysis for performance testing with ID {performance_testing_id}. "
        f"Risk Level: {performance_testing.risk_level}, "
    )
    await lock.release()
    logger.info(f"Released lock for performance testing {performance_testing_id}.")
