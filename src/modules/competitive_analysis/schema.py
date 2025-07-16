from pydantic import BaseModel, Field


class CompetitiveAnalysisCompareSummary(BaseModel):
    title: str = Field(..., description="Title of the summary")
    summary: str = Field(..., description="Summary of the competitive analysis item")
    icon: str | None = Field(
        None, description="Icon representing the competitive analysis item"
    )


class CompetitiveDeviceAnalysisKeyDifferenceResponse(BaseModel):
    title: str = Field(..., description="Title of the key difference")
    content: str = Field(
        ..., description="Content describing the key difference between devices"
    )
    icon: str | None = Field(None, description="Icon representing the key difference")


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


class CompetitiveAnalysisDetail(BaseModel):
    k_number: str = Field(
        "Not Available", description="FDA 510(k) K Number for the device, if available."
    )
    product_name: str = Field(
        "Not Available", description="Name of the product as registered with the FDA."
    )
    product_code: str = Field(
        "Not Available",
        description="FDA product code identifying the regulatory product category.",
    )
    regulation_number: str = Field(
        "Not Available", description="FDA regulation number for the device type."
    )
    classification: str = Field(
        "Not Available", description="FDA device classification."
    )
    prescription_otc: str = Field(
        "Not Available",
        description="Indicates if the device is Prescription Only, Over-the-counter (OTC), or other.",
    )
    predicate_device: str = Field(
        "Not Available",
        description="Name and K Number of predicate device(s) for FDA clearance; reference to previous device(s) if applicable.",
    )
    supplementary_data_source: str = Field(
        "Not Available",
        description="Web link or reference to package insert, FDA summary, or other official documentation used for data extraction.",
    )

    indications_for_use_statement: str = Field(
        "Not Available",
        description="Exact or paraphrased Indications for Use (IFU) statement describing the intended purpose, clinical indications, and limitations of the test.",
    )
    intended_use_population: str = Field(
        "Not Available",
        description="Description of patient/sample population for which the test is (intended).",
    )
    environment_of_use: str = Field(
        "Not Available", description="Intended setting for device use."
    )
    operating_conditions: str = Field(
        "Not Available",
        description="Temperature and handling conditions required for kit operation.",
    )
    storage_conditions: str = Field(
        "Not Available",
        description="Temperature and storage requirements for unopened kit and components.",
    )
    components_accessories: str = Field(
        "Not Available",
        description="List of all items supplied in the kit, including controls, reagents, strips/plates, package inserts, etc.",
    )

    measurand: str = Field(
        "Not Available", description="Targeted analyte(s) the test detects."
    )
    type_of_test: str = Field("Not Available", description="Test technology or format.")
    method: str = Field("Not Available", description="Overall method.")
    procedure: str = Field(
        "Not Available",
        description="Summary of test procedure and major steps (sample prep, incubations, reading, etc.).",
    )
    specimen_type: str = Field(
        "Not Available", description="Type of biological sample required."
    )
    controls: str = Field(
        "Not Available",
        description="Details on positive, negative, and cutoff controls provided or required for test validation.",
    )
    antigens: str = Field(
        "Not Available",
        description="Antigen types or specific proteins used for detection.",
    )
    sample_volume: str = Field(
        "Not Available", description="Volume of specimen required for one test or well."
    )
    reagents: str = Field(
        "Not Available",
        description="List of reagents and solutions provided in the kit.",
    )
    result_generation: str = Field(
        "Not Available", description="How test results are read or interpreted."
    )

    biocompatibility: str = Field(
        "Not Available",
        description="Whether any device component contacts the patient or sample directly; generally 'Not applicable' for in vitro diagnostics.",
    )
    sterility: str = Field("Not Available", description="Sterility status.")
    shelf_life: str = Field(
        "Not Available",
        description="Stability and usable life of the kit after opening or until expiration.",
    )
    electrical_mechanical_thermal_safety: str = Field(
        "Not Available",
        description="Statements on electrical, mechanical, or thermal safety, if the device includes such components; otherwise 'Not Defined'.",
    )
    electromagnetic_compatibility: str = Field(
        "Not Available",
        description="Statements on electromagnetic compatibility (EMC), if the device includes electronics; otherwise 'Not Defined'.",
    )
    software_testing: str = Field(
        "Not Available",
        description="Details on any software associated with the device, if relevant (often 'Not applicable').",
    )
    cybersecurity: str = Field(
        "Not Available",
        description="Details on cybersecurity considerations, if any software or connectivity is present (otherwise 'Not applicable').",
    )
    interoperability: str = Field(
        "Not Available",
        description="Details on interoperability with other instruments or data systems, if present (otherwise 'Not applicable').",
    )

    reproducibility: str = Field(
        "Not Available", description="Summary of reproducibility studies."
    )
    precision: str = Field(
        "Not Available", description="Summary of precision/within-lab studies."
    )
    analytical_specificity_interference: str = Field(
        "Not Available",
        description="Analytical specificity results, including healthy individuals in endemic/non-endemic areas; % specificity and n-values.",
    )
    cross_reactivity_study: str = Field(
        "Not Available",
        description="Summary of cross-reactivity findings for non-target infections or autoimmune markers; list diseases tested and any observed interference.",
    )
    interference_from_endogenous_analytes: str = Field(
        "Not Available",
        description="Study results for common endogenous interferents; describe if test performance is affected.",
    )
    assay_reportable_range: str = Field(
        "Not Available",
        description="Assay reportable range, if defined (typically 'Not applicable' for qualitative tests).",
    )
    traceability_stability_expected_values: str = Field(
        "Not Available",
        description="Any statements on traceability to standards, stability of reagents, or reference values expected in control/negative/positive populations.",
    )
    detection_limit: str = Field(
        "Not Available",
        description="Lowest level of analyte detectable if specified; otherwise 'Not applicable' or 'Not Defined'.",
    )
    assay_cutoff: str = Field(
        "Not Available",
        description="Definition and determination of assay cutoff for positivity; or state if not available.",
    )

    animal_testing_performance: str = Field(
        "Not Available",
        description="Animal testing data if any; otherwise, 'No animal testing performed' or 'Not applicable'.",
    )

    method_comparison_sttt: str = Field(
        "Not Available",
        description="Study comparing the device to Standard Two-Tier Test (STTT); summarize sample numbers, protocol, and key results.",
    )
    method_comparison_mttt: str = Field(
        "Not Available",
        description="Study comparing the device to Modified Two-Tier Test (MTTT); summarize sample numbers, protocol, and key results.",
    )
    clinical_sensitivity_specificity: str = Field(
        "Not Available",
        description="Clinical sensitivity/specificity performance, ideally broken out by disease stage, population, and compared to comparator methods.",
    )
    fresh_frozen_samples_comparison_study: str = Field(
        "Not Available",
        description="Study of test performance on fresh vs. frozen samples; summarize findings, concordance, and stability.",
    )
    antibody_class_specificity: str = Field(
        "Not Available", description="Specificity for antibody class."
    )
    clinical_cutoff: str = Field(
        "Not Available", description="Defined clinical cutoff if given."
    )
    expected_values_reference_range: str = Field(
        "Not Available",
        description="Expected values or reference range for target population as described in the IFU or clinical data; otherwise 'Not available'.",
    )
