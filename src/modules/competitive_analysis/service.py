from beanie import PydanticObjectId
from beanie.operators import In
from loguru import logger

from src.modules.competitive_analysis.model import (
    CompetitiveAnalysis,
    CompetitiveAnalysisDetail,
    to_competitive_analysis_detail_response,
)
from src.modules.competitive_analysis.schema import CompetitiveAnalysisDetailResponse


async def get_competitive_analysis(
    product_id: str,
) -> list[CompetitiveAnalysisDetailResponse]:
    competitive_analysis = await CompetitiveAnalysis.find(
        CompetitiveAnalysis.product_id == product_id
    ).to_list()
    competitive_analysis_detail_ids = [
        PydanticObjectId(analysis.competitive_analysis_detail_id) for analysis in competitive_analysis
    ]
    if competitive_analysis_detail_ids:
        competitive_analysis_details = await CompetitiveAnalysisDetail.find(
            In(CompetitiveAnalysisDetail.id, competitive_analysis_detail_ids)
        ).to_list()
        logger.info(
            f"Found {len(competitive_analysis_details)} competitive analysis details."
        )
    else:
        competitive_analysis_details = []
        logger.info("No competitive analysis details found.")
    if not competitive_analysis_details:
        logger.warning(f"No competitive analysis details for product_id={product_id}")
        return []

    competitive_analysis_details_map = {
        str(detail.id): detail for detail in competitive_analysis_details
    }
    return [
        to_competitive_analysis_detail_response(
            ca,
            competitive_analysis_details_map[ca.competitive_analysis_detail_id],
        )
        for ca in competitive_analysis
        if ca.competitive_analysis_detail_id in competitive_analysis_details_map
    ]
