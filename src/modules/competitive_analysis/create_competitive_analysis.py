from pathlib import Path
from src.modules.competitive_analysis.model import CompetitiveAnalysisDetail
from src.modules.competitive_analysis.schema import CompetitiveAnalysisDetailSchema
from src.services.openai.extract_files_data import extract_files_data


system_instruction = """
You are an FDA regulatory expert. Based on the provided document, extract all relevant information and return a single `CompetitiveAnalysisDetail` JSON object.

Follow the schema strictly. For any field not present or applicable, return "Not Available" as the value.
Do not include any explanations, notes, or extra text—only return the structured JSON object.

Schema Fields (summary):
- Regulatory & Identity: k_number, product_name, regulatory_pathway, product_code, regulation_number, classification, prescription_otc, predicate_device, supplementary_data_source
- Intended Use & Environment: indications_for_use_statement, intended_use_population, environment_of_use, operating_conditions, storage_conditions, components_accessories
- Test Description: measurand, type_of_test, method, procedure, specimen_type, controls, antigens, sample_volume, reagents, result_generation
- Safety & Compatibility: biocompatibility, sterility, shelf_life, electrical_mechanical_thermal_safety, electromagnetic_compatibility, software_testing, cybersecurity, interoperability
- Analytical Performance: reproducibility, precision, analytical_specificity_interference, cross_reactivity_study, interference_from_endogenous_analytes, assay_reportable_range, traceability_stability_expected_values, detection_limit, assay_cutoff
- Clinical Performance: animal_testing_performance, method_comparison_sttt, method_comparison_mttt, clinical_sensitivity_specificity, fresh_frozen_samples_comparison_study, antibody_class_specificity, clinical_cutoff, expected_values_reference_range

Ensure every field is included in the output, even if its value is "Not Available". Use only factual content from the document—no assumptions or extrapolations.
"""


user_question = """
Please extract all relevant information for the competitive analysis from the provided documents and return a JSON object matching the CompetitiveAnalysisDetail schema.
"""


async def create_competitive_analysis(
    product_simple_name: str,
    document_paths: list[Path],
    confidence_score: float,
    use_system_data: bool,
) -> CompetitiveAnalysisDetail:
    sources = [path.name for path in document_paths]
    result = await extract_files_data(
        file_paths=document_paths,
        system_instruction=system_instruction,
        user_question=user_question,
        model_class=CompetitiveAnalysisDetailSchema,
    )
    competitive_analysis_detail = CompetitiveAnalysisDetail(
        product_simple_name=product_simple_name,
        confidence_score=confidence_score,
        sources=sources,
        use_system_data=use_system_data,
        **result.model_dump(),
    )
    return competitive_analysis_detail
