from datetime import datetime
from beanie import Document, PydanticObjectId
from src.modules.competitive_analysis.schema import (
    CompetitiveAnalysisDetailBase,
    CompetitiveAnalysisSource,
)


class CompetitiveAnalysis(Document):
    product_id: str
    competitive_analysis_detail_id: str
    is_self_analysis: bool

    class Settings:
        name = "competitive_analysis"

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }


class CompetitiveAnalysisDetail(Document, CompetitiveAnalysisDetailBase):
    product_simple_name: str
    confidence_score: float
    sources: list[CompetitiveAnalysisSource]
    is_ai_generated: bool
    use_system_data: bool

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
