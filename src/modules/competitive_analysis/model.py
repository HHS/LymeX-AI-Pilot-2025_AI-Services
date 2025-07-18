from datetime import datetime

from beanie import Document, PydanticObjectId

from src.modules.competitive_analysis.schema import (
    CompetitiveAnalysisCompareSummary,
    CompetitiveAnalysisDetail,
    CompetitiveDeviceAnalysisKeyDifferenceResponse,
)
from src.modules.product_profile.schema import Feature, Performance


class CompetitiveAnalysis(Document):
    reference_product_id: str
    product_name: str
    category: str
    regulatory_pathway: str
    clinical_study: str
    fda_approved: bool
    ce_marked: bool
    device_ifu_description: str
    key_differences: list[CompetitiveDeviceAnalysisKeyDifferenceResponse]
    recommendations: list[str]
    features: list[Feature]
    claims: list[str]
    reference_number: str
    confidence_score: float
    sources: list[str]
    performance: Performance
    price: int
    your_product_summary: CompetitiveAnalysisCompareSummary
    competitor_summary: CompetitiveAnalysisCompareSummary
    instructions: list[str]
    type_of_use: str
    your_product: CompetitiveAnalysisDetail
    competitor: CompetitiveAnalysisDetail
    is_ai_generated: bool = False
    use_system_data: bool = False

    class Settings:
        name = "competitive_analysis"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

class CompetitiveAnalysis1(Document):
    your_product_summary: CompetitiveAnalysisCompareSummary
    class Settings:
        name = "competitive_analysis"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class AnalyzeCompetitiveAnalysisProgress(Document):
    reference_product_id: str
    total_files: int
    processed_files: int
    updated_at: datetime

    class Settings:
        name = "analyze_competitive_analysis_progress"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }
