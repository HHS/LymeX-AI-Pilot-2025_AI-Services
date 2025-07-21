"""
Shared progress-tracking helper for background jobs in claims builder.
"""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import HTTPException
from loguru import logger

from .model import AnalyzeClaimBuilderProgress


class AnalyzeProgress:
    """Persist progress to Mongo via Beanie and expose incr / complete helpers."""

    def __init__(self) -> None:
        self._progress: AnalyzeClaimBuilderProgress | None = None

    # --------------------------------------------------------------------- #
    # life‑cycle helpers
    # --------------------------------------------------------------------- #

    async def init(self, *, product_id: str, total_files: int) -> None:
        """
        Create—or reset—an AnalyzeClaimBuilderProgress document for *product_id*.
        """
        now = datetime.now(timezone.utc)
        existing = await AnalyzeClaimBuilderProgress.find_one(
            AnalyzeClaimBuilderProgress.product_id == product_id
        )

        if existing:
            existing.total_files = total_files
            existing.processed_files = 0
            existing.updated_at = now
            self._progress = existing
        else:
            self._progress = AnalyzeClaimBuilderProgress(
                product_id=product_id,
                total_files=total_files,
                processed_files=0,
                updated_at=now,
            )
        await self._progress.save()
        logger.info("Progress initialised for {} ({} files)", product_id, total_files)

    async def incr(self, n: int = 1) -> None:
        """Increase *processed_files* and persist."""
        if not self._progress:
            raise HTTPException(500, "Progress not initialised")

        self._progress.processed_files += n
        self._progress.updated_at = datetime.now(timezone.utc)
        await self._progress.save()

    async def complete(self) -> None:
        """Mark job as finished."""
        if self._progress:
            self._progress.processed_files = self._progress.total_files
            self._progress.updated_at = datetime.now(timezone.utc)
            await self._progress.save()
            logger.info("Progress complete for {}", self._progress.product_id)
