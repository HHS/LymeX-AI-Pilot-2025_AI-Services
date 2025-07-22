from datetime import datetime, timezone
from loguru import logger

from src.modules.regulatory_pathway.model import AnalyzeRegulatoryPathwayProgress


class AnalyzeProgress:
    def __init__(self):
        self.progress: AnalyzeRegulatoryPathwayProgress | None = None

    async def initialize(self, product_id: str, total_files: int):
        existing = await AnalyzeRegulatoryPathwayProgress.find_one(
            AnalyzeRegulatoryPathwayProgress.product_id == product_id
        )
        now = datetime.now(timezone.utc)
        if existing:
            existing.total_files = total_files
            existing.processed_files = 0
            existing.updated_at = now
            self.progress = existing
        else:
            self.progress = AnalyzeRegulatoryPathwayProgress(
                product_id=product_id,
                total_files=total_files,
                processed_files=0,
                updated_at=now,
            )
        await self.progress.save()
        logger.info(f"Progress initialized for {product_id}: {total_files} files")

    async def complete(self):
        if not self.progress:
            return
        self.progress.processed_files = self.progress.total_files
        self.progress.updated_at = datetime.now(timezone.utc)
        await self.progress.save()
        logger.info(f"Progress complete for {self.progress.product_id}")
