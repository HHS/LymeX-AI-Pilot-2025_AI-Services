from datetime import datetime, timezone
from loguru import logger

from src.modules.competitive_analysis.model import AnalyzeCompetitiveAnalysisProgress


class AnalyzeProgress:
    initialized = False
    progress: AnalyzeCompetitiveAnalysisProgress

    async def initialize(self, product_id: str, total_files: int):
        logger.info(
            f"Initializing progress for product_id={product_id}, total_files={total_files}"
        )
        existing_progress = await AnalyzeCompetitiveAnalysisProgress.find_one(
            AnalyzeCompetitiveAnalysisProgress.product_id == product_id,
        )
        if existing_progress:
            logger.info(
                f"Existing progress found for product_id={product_id}, resetting processed_files to 0"
            )
            self.progress = existing_progress
            self.progress.product_id = product_id
            self.progress.total_files = total_files
            self.progress.processed_files = 0
            self.progress.updated_at = datetime.now(timezone.utc)
        else:
            logger.info(
                f"No existing progress found for product_id={product_id}, creating new progress entry"
            )
            self.progress = AnalyzeCompetitiveAnalysisProgress(
                product_id=product_id,
                total_files=total_files,
                processed_files=0,
                updated_at=datetime.now(timezone.utc),
            )
        await self.progress.save()
        self.initialized = True
        logger.info(
            f"Initialized progress for product {product_id} with total files {total_files}"
        )

    async def complete(self):
        if not self.progress:
            return
        self.progress.processed_files = self.progress.total_files
        self.progress.updated_at = datetime.now(timezone.utc)
        await self.progress.save()
        logger.info(f"Progress complete for {self.progress.product_id}")
