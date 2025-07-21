from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

from src.modules.claim_builder.schema import (
    IFU,
    Issue,
    Compliance,
    Draft,
    MissingElement,
    PhraseConflict,
    RiskIndicator,
)


class ClaimBuilder(Document):
    product_id: str
    draft: list[Draft]
    key_phrases: list[str]
    ifu: list[IFU]
    compliance: list[Compliance]
    missing_elements: list[MissingElement]
    risk_indicators: list[RiskIndicator]
    phrase_conflicts: list[PhraseConflict]
    issues: list[Issue] = []                  #new
    is_user_input: bool = False
    user_acceptance: bool = False

    class Settings:
        name = "claim_builder"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class AnalyzeClaimBuilderProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_claim_builder_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
