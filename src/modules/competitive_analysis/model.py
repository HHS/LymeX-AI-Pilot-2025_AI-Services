from datetime import datetime

from beanie import Document, PydanticObjectId
from src.modules.competitive_analysis.schema import (
    CompetitiveAnalysisDetailBase,
    CompetitiveAnalysisDetailResponse,
    CompetitiveAnalysisDetailSchema,
    CompetitiveAnalysisSource,
)
from src.modules.product.model import Product
from src.modules.product_profile.model import ProductProfile
from src.modules.product_profile.schema import Feature, Performance


class CompetitiveAnalysis(Document):
    product_id: str
    competitive_analysis_detail_id: str
    is_self_analysis: bool

    accepted: bool | None = None
    accept_reject_reason: str | None = None
    accept_reject_by: str | None = None

    class Settings:
        name = "competitive_analysis"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class CompetitiveAnalysisDetail(Document, CompetitiveAnalysisDetailBase):
    document_hash: str
    document_names: list[str]
    product_simple_name: str
    confidence_score: float
    sources: list[CompetitiveAnalysisSource]
    is_ai_generated: bool
    use_system_data: bool
    data_type: str

    class Settings:
        name = "competitive_analysis_detail"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class AnalyzeCompetitiveAnalysisProgress(Document):
    product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_competitive_analysis_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


def to_competitive_analysis_detail_response(
    ca: CompetitiveAnalysis,
    detail: CompetitiveAnalysisDetail,
) -> CompetitiveAnalysisDetailResponse:
    return CompetitiveAnalysisDetailResponse(
        id=str(ca.id),
        product_id=ca.product_id,
        is_self_analysis=ca.is_self_analysis,
        details=CompetitiveAnalysisDetailSchema(
            **detail.model_dump(),
        ),
    )
