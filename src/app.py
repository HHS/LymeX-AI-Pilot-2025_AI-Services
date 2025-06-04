from fastapi import FastAPI

from src.modules.claim_builder.analyze import analyze_claim_builder
from src.modules.claim_builder.schema import ClaimBuilder
from src.modules.clinical_trial.analyze import analyze_clinical_trial
from src.modules.clinical_trial.schema import ClinicalTrial
from src.modules.regulatory_pathway.analyze import analyze_regulatory_pathway
from src.modules.regulatory_pathway.schema import RegulatoryPathway
from src.modules.test_comparison.analyze import analyze_test_comparison
from src.modules.test_comparison.schema import TestComparison


app = FastAPI(
    title="AI Service",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Service!"}


@app.get("/claim-builder")
async def claim_builder_handler(
    product_id: str,
) -> ClaimBuilder:
    claim_builder = await analyze_claim_builder(product_id)
    return claim_builder


@app.get("/clinical-trial")
async def clinical_trial_handler(
    product_id: str,
) -> list[ClinicalTrial]:
    clinical_trial = await analyze_clinical_trial(product_id)
    return clinical_trial


@app.get("/regulatory-pathway")
async def regulatory_pathway_handler(
    product_id: str,
) -> RegulatoryPathway:
    regulatory_pathway = await analyze_regulatory_pathway(product_id)
    return regulatory_pathway


@app.get("/test-comparison")
async def test_comparison_handler(
    product_id: str,
) -> list[TestComparison]:
    test_comparison = await analyze_test_comparison(product_id)
    return test_comparison
