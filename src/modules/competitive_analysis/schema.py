from pydantic import BaseModel, Field

class CompetitiveAnalysisDocumentResponse(BaseModel):
    document_name: str = Field(
        ..., description="Name of the competitive analysis document"
    )
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    competitor_name: str = Field(..., description="Name of the competitor")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    content_type: str = Field(..., description="Content type of the document")
    size: int = Field(..., description="Size of the document in bytes")
    key: str = Field(..., description="Key of the document in the storage system")
    path: str = Field(..., description="Path to the document in the local machine")


class CompetitiveAnalysisDetailBase:
    k_number: str = Field(
        ..., description="FDA 510(k) K Number for the device, if available."
    )
    product_name: str = Field(..., description="Product Name or Device Name")
    regulatory_pathway: str = Field(
        ...,
        description="Regulatory Pathway, one of the following: 510(k), PMA, De Novo, Exempt",
    )
    product_code: str = Field(
        ...,
        description="FDA product code identifying the regulatory product category.",
    )
    regulation_number: str = Field(
        ..., description="FDA regulation number for the device type."
    )
    classification: str = Field(..., description="FDA device classification.")
    fda_cleared: bool | None = Field(
        None, description="FDA clearance status (None if not applicable)"
    )
    fda_approved: bool | None = Field(
        None, description="FDA approval status (None if not applicable)"
    )
    ce_marked: bool | None = Field(
        None, description="CE marking status (None if not applicable)"
    )
    prescription_otc: str = Field(
        ...,
        description="Indicates if the device is Prescription Only, Over-the-counter (OTC), or other.",
    )
    predicate_device: str = Field(
        ...,
        description="Name and K Number of predicate device(s) for FDA clearance; reference to previous device(s) if applicable.",
    )
    supplementary_data_source: str = Field(
        ...,
        description="Web link or reference to package insert, FDA summary, or other official documentation used for data extraction.",
    )
    indications_for_use_statement: str = Field(
        ...,
        description="Exact or paraphrased Indications for Use (IFU) statement describing the intended purpose, clinical indications, and limitations of the test.",
    )
    intended_use_population: str = Field(
        ...,
        description="Description of patient/sample population for which the test is (intended).",
    )
    environment_of_use: str = Field(..., description="Intended setting for device use.")
    operating_conditions: str = Field(
        ...,
        description="Temperature and handling conditions required for kit operation.",
    )
    storage_conditions: str = Field(
        ...,
        description="Temperature and storage requirements for unopened kit and components.",
    )
    components_accessories: str = Field(
        ...,
        description="List of all items supplied in the kit, including controls, reagents, strips/plates, package inserts, etc.",
    )
    measurand: str = Field(..., description="Targeted analyte(s) the test detects.")
    instructions: str = Field(
        ...,
        description="Instructions for use, including preparation, sample collection, and test execution.",
    )
    type_of_test: str = Field(..., description="Test technology or format.")
    type_of_use: str = Field(
        ...,
        description="Type of use, e.g., qualitative, semi-quantitative, quantitative.",
    )
    method: str = Field(..., description="Overall method.")
    procedure: str = Field(
        ...,
        description="Summary of test procedure and major steps (sample prep, incubations, reading, etc.).",
    )
    specimen_type: str = Field(..., description="Type of biological sample required.")
    controls: str = Field(
        ...,
        description="Details on positive, negative, and cutoff controls provided or required for test validation.",
    )
    antigens: str = Field(
        ...,
        description="Antigen types or specific proteins used for detection.",
    )
    sample_volume: str = Field(
        ..., description="Volume of specimen required for one test or well."
    )
    reagents: str = Field(
        ...,
        description="List of reagents and solutions provided in the kit.",
    )
    result_generation: str = Field(
        ..., description="How test results are read or interpreted."
    )
    biocompatibility: str = Field(
        ...,
        description="Whether any device component contacts the patient or sample directly; generally 'Not applicable' for in vitro diagnostics.",
    )
    sterility: str = Field(..., description="Sterility status.")
    shelf_life: str = Field(
        ...,
        description="Stability and usable life of the kit after opening or until expiration.",
    )
    electrical_mechanical_thermal_safety: str = Field(
        ...,
        description="Statements on electrical, mechanical, or thermal safety, if the device includes such components; otherwise 'Not Defined'.",
    )
    electromagnetic_compatibility: str = Field(
        ...,
        description="Statements on electromagnetic compatibility (EMC), if the device includes electronics; otherwise 'Not Defined'.",
    )
    software_testing: str = Field(
        ...,
        description="Details on any software associated with the device, if relevant (often 'Not applicable').",
    )
    cybersecurity: str = Field(
        ...,
        description="Details on cybersecurity considerations, if any software or connectivity is present (otherwise 'Not applicable').",
    )
    interoperability: str = Field(
        ...,
        description="Details on interoperability with other instruments or data systems, if present (otherwise 'Not applicable').",
    )
    reproducibility: str = Field(..., description="Summary of reproducibility studies.")
    precision: str = Field(..., description="Summary of precision/within-lab studies.")
    analytical_specificity_interference: str = Field(
        ...,
        description="Analytical specificity results, including healthy individuals in endemic/non-endemic areas; % specificity and n-values.",
    )
    cross_reactivity_study: str = Field(
        ...,
        description="Summary of cross-reactivity findings for non-target infections or autoimmune markers; list diseases tested and any observed interference.",
    )
    interference_from_endogenous_analytes: str = Field(
        ...,
        description="Study results for common endogenous interferents; describe if test performance is affected.",
    )
    assay_reportable_range: str = Field(
        ...,
        description="Assay reportable range, if defined (typically 'Not applicable' for qualitative tests).",
    )
    traceability_stability_expected_values: str = Field(
        ...,
        description="Any statements on traceability to standards, stability of reagents, or reference values expected in control/negative/positive populations.",
    )
    detection_limit: str = Field(
        ...,
        description="Lowest level of analyte detectable if specified; otherwise 'Not applicable' or 'Not Defined'.",
    )
    assay_cutoff: str = Field(
        ...,
        description="Definition and determination of assay cutoff for positivity; or state if not available.",
    )
    animal_testing_performance: str = Field(
        ...,
        description="Animal testing data if any; otherwise, 'No animal testing performed' or 'Not applicable'.",
    )
    method_comparison_sttt: str = Field(
        ...,
        description="Study comparing the device to Standard Two-Tier Test (STTT); summarize sample numbers, protocol, and key results.",
    )
    method_comparison_mttt: str = Field(
        ...,
        description="Study comparing the device to Modified Two-Tier Test (MTTT); summarize sample numbers, protocol, and key results.",
    )
    clinical_sensitivity_specificity: str = Field(
        ...,
        description="Clinical sensitivity/specificity performance, ideally broken out by disease stage, population, and compared to comparator methods.",
    )
    fresh_frozen_samples_comparison_study: str = Field(
        ...,
        description="Study of test performance on fresh vs. frozen samples; summarize findings, concordance, and stability.",
    )
    antibody_class_specificity: str = Field(
        ..., description="Specificity for antibody class."
    )
    clinical_cutoff: str = Field(..., description="Defined clinical cutoff if given.")
    expected_values_reference_range: str = Field(
        ...,
        description="Expected values or reference range for target population as described in the IFU or clinical data; otherwise 'Not available'.",
    )


class CompetitiveAnalysisDetailSchema(BaseModel, CompetitiveAnalysisDetailBase): ...


class CompetitiveAnalysisSource(BaseModel):
    name: str = Field(..., description="Name of the source")
    key: str = Field(..., description="S3 key for the source document")


class CompetitiveAnalysisDetailResponse(BaseModel):
    id: str = Field(
        ..., description="Unique identifier for the competitive analysis detail"
    )
    product_id: str = Field(
        ..., description="ID of the product this analysis is related to"
    )
    is_self_analysis: bool = Field(
        ..., description="Indicates if this analysis is a self-analysis"
    )
    details: CompetitiveAnalysisDetailSchema = Field(
        ..., description="Detailed information about the competitive analysis"
    )
