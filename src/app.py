from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from src.infrastructure.database import init_db
from src.modules.claim_builder.analyze import analyze_claim_builder
from src.modules.clinical_trial.analyze import analyze_clinical_trial
from src.modules.competitive_analysis.analyze import analyze_competitive_analysis
from src.modules.competitive_analysis.schema import CompetitiveAnalysisDetailResponse
from src.modules.competitive_analysis.service import get_competitive_analysis
from src.modules.index_system_data.analyze import (
    index_system_data,
)
from src.modules.performance_testing.analyze import (
    run_all_performance_tests,
    run_performance_test_card,
)
from src.modules.product_profile.analyze import analyze_product_profile
from src.modules.regulatory_background.analyze import analyze_regulatory_background
from src.modules.regulatory_pathway.analyze import analyze_regulatory_pathway
from src.modules.test_comparison.analyze import analyze_test_comparison
from src.modules.checklist.analyze import analyze_checklist


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # Add any cleanup logic here if needed


app = FastAPI(title="AI Service", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Service!"}


@app.post("/analyze-claim-builder")
async def analyze_claim_builder_handler(
    product_id: str,
) -> None:
    await analyze_claim_builder(product_id)


@app.post("/analyze-clinical-trial")
async def analyze_clinical_trial_handler(
    product_id: str,
) -> None:
    await analyze_clinical_trial(product_id)


@app.post("/analyze-competitive-analysis")
async def analyze_competitive_analysis_handler(
    product_id: str,
) -> None:
    await analyze_competitive_analysis(product_id)


@app.post("/analyze-performance-testing")
async def analyze_performance_testing_handler(
    product_id: str,
    performance_testing_id: str | None = None,
) -> None:
    if performance_testing_id:
        await run_performance_test_card(product_id, performance_testing_id)
    else:
        await run_all_performance_tests(product_id)
        await run_all_performance_tests(product_id)


@app.post("/analyze-product-profile")
async def analyze_product_profile_handler(
    product_id: str,
) -> None:
    await analyze_product_profile(product_id)


@app.post("/analyze-regulatory-background")
async def analyze_regulatory_background_handler(
    product_id: str,
) -> None:
    await analyze_regulatory_background(product_id)


@app.post("/analyze-regulatory-pathway")
async def analyze_regulatory_pathway_handler(
    product_id: str,
) -> None:
    await analyze_regulatory_pathway(product_id)


@app.post("/analyze-test-comparison")
async def analyze_test_comparison_handler(
    product_id: str,
) -> None:
    await analyze_test_comparison(product_id)


@app.post("/analyze-checklist")
async def analyze_checklist_handler(
    product_id: str,
) -> None:
    await analyze_checklist(product_id)


@app.post("/index-system-data")
async def index_system_data_handler() -> None:
    await index_system_data()


@app.get("/competitive-analysis/{product_id}")
async def competitive_analysis_handler(
    product_id: str,
) -> list[CompetitiveAnalysisDetailResponse]:
    return await get_competitive_analysis(product_id)
