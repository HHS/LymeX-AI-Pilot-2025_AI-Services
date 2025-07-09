from datetime import datetime
from pydantic import BaseModel, Field

from src.modules.product_profile.schema import Feature, Performance


# ============================
# Competitive Analysis Request
# ============================


class UpdateCompetitiveAnalysisRequest(BaseModel):
    product_name: str | None = Field(None, description="Name of the product")
    category: str | None = Field(
        None, description="Category of the competitive analysis"
    )
    regulatory_pathway: str | None = Field(
        None, description="Regulatory pathway for the product"
    )
    clinical_study: str | None = Field(
        None, description="Clinical study information for the product"
    )
    fda_approved: bool | None = Field(
        None, description="Indicates if the product is FDA approved"
    )
    ce_marked: bool | None = Field(
        None, description="Indicates if the product is CE marked"
    )
    is_ai_generated: bool | None = Field(
        None, description="Indicates if the analysis is AI generated"
    )


class UploadTextInputDocumentRequest(BaseModel):
    text: str = Field(..., description="Text input for the document")
    category: str = Field(..., description="Category of the document")


# ============================
# Competitive Analysis Response
# ============================


class CompetitiveAnalysisResponse(BaseModel):
    id: str = Field(..., description="ID of the competitive analysis")
    product_name: str = Field(..., description="Name of the product")
    reference_number: str = Field(
        ..., description="Reference Number of the competitive analysis"
    )
    regulatory_pathway: str = Field(
        ..., description="Regulatory pathway for the product"
    )
    fda_approved: bool = Field(
        ..., description="Indicates if the product is FDA approved"
    )
    ce_marked: bool = Field(..., description="Indicates if the product is CE marked")
    is_ai_generated: bool = Field(
        ..., description="Indicates if the analysis is AI generated"
    )
    confidence_score: float = Field(
        ..., description="Confidence score of the competitive analysis"
    )
    sources: list[str] = Field(
        ..., description="List of sources for the competitive analysis"
    )


class CompetitiveAnalysisDetailResponse(BaseModel): ...


class CompetitiveAnalysisCompareSummary(BaseModel):
    title: str = Field(..., description="Title of the summary")
    summary: str = Field(..., description="Summary of the competitive analysis item")
    icon: str | None = Field(
        None, description="Icon representing the competitive analysis item"
    )


class CompetitiveAnalysisCompareItemResponse(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    price: int = Field(..., description="Price of the product")
    features: list[Feature] = Field(..., description="List of features of the product")
    performance: Performance = Field(
        ..., description="Performance metrics of the product"
    )
    summary: CompetitiveAnalysisCompareSummary = Field(
        ..., description="Summary of the competitive analysis item"
    )


class CompetitiveAnalysisCompareResponse(BaseModel):
    your_product: CompetitiveAnalysisCompareItemResponse = Field(
        ..., description="Details of your product in the competitive analysis"
    )
    competitor: CompetitiveAnalysisCompareItemResponse = Field(
        ..., description="Details of the competitor product in the competitive analysis"
    )


class CompetitiveDeviceAnalysisItemResponse(BaseModel):
    id: str = Field(..., description="ID of the device analysis item")
    content: str = Field(..., description="Content of the device analysis item")
    instructions: list[str] = Field(
        ..., description="List of instructions for the device analysis item"
    )
    type_of_use: str = Field(
        ..., description="Type of use for the device (e.g., diagnostic, therapeutic)"
    )
    fda_approved: bool = Field(
        ..., description="Indicates if the device is FDA approved"
    )
    ce_marked: bool = Field(..., description="Indicates if the device is CE marked")


class CompetitiveDeviceAnalysisKeyDifferenceResponse(BaseModel):
    title: str = Field(..., description="Title of the key difference")
    content: str = Field(
        ..., description="Content describing the key difference between devices"
    )
    icon: str | None = Field(None, description="Icon representing the key difference")


class CompetitiveDeviceAnalysisResponse(BaseModel):
    your_device: CompetitiveDeviceAnalysisItemResponse = Field(
        ..., description="Details of your device in the competitive analysis"
    )
    competitor_device: CompetitiveDeviceAnalysisItemResponse = Field(
        ..., description="Details of the competitor device in the competitive analysis"
    )
    key_differences: list[CompetitiveDeviceAnalysisKeyDifferenceResponse] = Field(
        ..., description="List of key differences between the devices"
    )
    recommendations: list[str] = Field(
        ..., description="List of recommendations based on the competitive analysis"
    )


class CompetitiveAnalysisDocumentResponse(BaseModel):
    document_name: str = Field(
        ..., description="Name of the competitive analysis document"
    )
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    category: str = Field(..., description="Category of the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    content_type: str = Field(
        ..., description="Content type of the document (e.g., PDF, DOCX)"
    )
    size: int = Field(..., description="Size of the document in bytes")


class AnalyzeCompetitiveAnalysisProgressResponse(BaseModel):
    reference_product_id: str = Field(..., description="ID of the reference product")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(
        ..., description="Number of files that have been processed"
    )
    updated_at: datetime = Field(
        ..., description="Date and time when the progress was last updated"
    )


class CompetitiveAnalysisDetail(BaseModel):
    k_number: str = Field(
        "Not Available",
        description="FDA 510(k) K Number for the device, if available (e.g., K233367)."
    )
    product_code: str = Field(
        "Not Available",
        description="FDA product code (e.g., LSR) identifying the regulatory product category."
    )
    regulation_number: str = Field(
        "Not Available",
        description="FDA regulation number for the device type (e.g., 866.3830)."
    )
    classification: str = Field(
        "Not Available",
        description="FDA device classification (e.g., Class 2)."
    )
    prescription_otc: str = Field(
        "Not Available",
        description="Indicates if the device is Prescription Only, Over-the-counter (OTC), or other."
    )
    predicate_device: str = Field(
        "Not Available",
        description="Name and K Number of predicate device(s) for FDA clearance; reference to previous device(s) if applicable."
    )
    supplementary_data_source: str = Field(
        "Not Available",
        description="Web link or reference to package insert, FDA summary, or other official documentation used for data extraction."
    )

    indications_for_use_statement: str = Field(
        "Not Available",
        description="Exact or paraphrased Indications for Use (IFU) statement describing the intended purpose, clinical indications, and limitations of the test."
    )
    intended_use_population: str = Field(
        "Not Available",
        description="Description of patient/sample population for which the test is intended (e.g., symptomatic, suspected Lyme disease patients, etc.)."
    )
    environment_of_use: str = Field(
        "Not Available",
        description="Intended setting for device use (e.g., Clinical Laboratory, Point-of-care)."
    )
    operating_conditions: str = Field(
        "Not Available",
        description="Temperature and handling conditions required for kit operation (e.g., 15–30°C or 59–86°F, bring to room temp before use)."
    )
    storage_conditions: str = Field(
        "Not Available",
        description="Temperature and storage requirements for unopened kit and components (e.g., 2–8°C)."
    )
    components_accessories: str = Field(
        "Not Available",
        description="List of all items supplied in the kit, including controls, reagents, strips/plates, package inserts, etc."
    )

    measurand: str = Field(
        "Not Available",
        description="Targeted analyte(s) the test detects (e.g., IgG and/or IgM antibodies to Borrelia burgdorferi)."
    )
    type_of_test: str = Field(
        "Not Available",
        description="Test technology or format (e.g., ImmunoBlot, ELISA, Microarray)."
    )
    method: str = Field(
        "Not Available",
        description="Overall method (e.g., qualitative detection, microarray, antigen-coated wells)."
    )
    procedure: str = Field(
        "Not Available",
        description="Summary of test procedure and major steps (sample prep, incubations, reading, etc.)."
    )
    specimen_type: str = Field(
        "Not Available",
        description="Type of biological sample required (e.g., serum)."
    )
    controls: str = Field(
        "Not Available",
        description="Details on positive, negative, and cutoff controls provided or required for test validation."
    )
    antigens: str = Field(
        "Not Available",
        description="Antigen types or specific proteins used for detection (e.g., VlsE, OspC, 93 kD, etc.)."
    )
    sample_volume: str = Field(
        "Not Available",
        description="Volume of specimen required for one test or well (e.g., 10 µL, 100 µL)."
    )
    reagents: str = Field(
        "Not Available",
        description="List of reagents and solutions provided in the kit (e.g., diluent, wash buffer, conjugate, substrate)."
    )
    result_generation: str = Field(
        "Not Available",
        description="How test results are read or interpreted (e.g., manual reading, automated reader, spectrophotometer, etc.)."
    )

    biocompatibility: str = Field(
        "Not Available",
        description="Whether any device component contacts the patient or sample directly; generally 'Not applicable' for in vitro diagnostics."
    )
    sterility: str = Field(
        "Not Available",
        description="Sterility status (e.g., single-use non-sterile, sterile, or not defined in sources)."
    )
    shelf_life: str = Field(
        "Not Available",
        description="Stability and usable life of the kit after opening or until expiration (e.g., 'Opened kit stable for 6 months')."
    )
    electrical_mechanical_thermal_safety: str = Field(
        "Not Available",
        description="Statements on electrical, mechanical, or thermal safety, if the device includes such components; otherwise 'Not Defined'."
    )
    electromagnetic_compatibility: str = Field(
        "Not Available",
        description="Statements on electromagnetic compatibility (EMC), if the device includes electronics; otherwise 'Not Defined'."
    )
    software_testing: str = Field(
        "Not Available",
        description="Details on any software associated with the device, if relevant (often 'Not applicable')."
    )
    cybersecurity: str = Field(
        "Not Available",
        description="Details on cybersecurity considerations, if any software or connectivity is present (otherwise 'Not applicable')."
    )
    interoperability: str = Field(
        "Not Available",
        description="Details on interoperability with other instruments or data systems, if present (otherwise 'Not applicable')."
    )

    reproducibility: str = Field(
        "Not Available",
        description="Summary of reproducibility studies (e.g., multi-site, multi-operator, blinded panels, number of sites, operators, days, runs, and performance results)."
    )
    precision: str = Field(
        "Not Available",
        description="Summary of precision/within-lab studies (e.g., duplicate runs, days, standard deviation, CV%, samples tested)."
    )
    analytical_specificity_interference: str = Field(
        "Not Available",
        description="Analytical specificity results, including healthy individuals in endemic/non-endemic areas; % specificity and n-values."
    )
    cross_reactivity_study: str = Field(
        "Not Available",
        description="Summary of cross-reactivity findings for non-target infections or autoimmune markers; list diseases tested and any observed interference."
    )
    interference_from_endogenous_analytes: str = Field(
        "Not Available",
        description="Study results for common endogenous interferents (e.g., hemoglobin, bilirubin, triglycerides); describe if test performance is affected."
    )
    assay_reportable_range: str = Field(
        "Not Available",
        description="Assay reportable range, if defined (typically 'Not applicable' for qualitative tests)."
    )
    traceability_stability_expected_values: str = Field(
        "Not Available",
        description="Any statements on traceability to standards, stability of reagents, or reference values expected in control/negative/positive populations."
    )
    detection_limit: str = Field(
        "Not Available",
        description="Lowest level of analyte detectable if specified; otherwise 'Not applicable' or 'Not Defined'."
    )
    assay_cutoff: str = Field(
        "Not Available",
        description="Definition and determination of assay cutoff for positivity (e.g., mean + 2SD, ROC analysis); or state if not available."
    )

    animal_testing_performance: str = Field(
        "Not Available",
        description="Animal testing data if any; otherwise, 'No animal testing performed' or 'Not applicable'."
    )

    method_comparison_sttt: str = Field(
        "Not Available",
        description="Study comparing the device to Standard Two-Tier Test (STTT); summarize sample numbers, protocol, and key results."
    )
    method_comparison_mttt: str = Field(
        "Not Available",
        description="Study comparing the device to Modified Two-Tier Test (MTTT); summarize sample numbers, protocol, and key results."
    )
    clinical_sensitivity_specificity: str = Field(
        "Not Available",
        description="Clinical sensitivity/specificity performance, ideally broken out by disease stage, population, and compared to comparator methods."
    )
    fresh_frozen_samples_comparison_study: str = Field(
        "Not Available",
        description="Study of test performance on fresh vs. frozen samples; summarize findings, concordance, and stability."
    )
    antibody_class_specificity: str = Field(
        "Not Available",
        description="Specificity for antibody class (e.g., study confirming IgG-only detection, no cross-reaction with IgM, etc.)."
    )
    clinical_cutoff: str = Field(
        "Not Available",
        description="Defined clinical cutoff if given (e.g., 'mean plus two SD', 'determined by ROC curve', or 'Not available')."
    )
    expected_values_reference_range: str = Field(
        "Not Available",
        description="Expected values or reference range for target population as described in the IFU or clinical data; otherwise 'Not available'."
    )