from typing import Literal, TypedDict


class QuestionJson(TypedDict):
    section: str
    question_number: int
    question: str
    question_type: Literal["checkbox", "radio", "text", "boolean"]
    options: list[str] | None
    key_phases: str | None


questions: list[QuestionJson] = [
    {
        "section": "product_profile",
        "question_number": 1,
        "question": "This device could be described as (check all that apply):",
        "question_type": "checkbox",
        "options": [
            "Instrument",
            "Assay",
        ],
        "key_phases": """
Assay (specific test or procedure used to detect/measure/identify a substances or analyte):
    - In vitro qualitative detection
    - assay/test/methodology
    - screening

Instrument (device used to perform the assay):
    - Test reagents
    - Test kit
    - Test System
""",
    },
    {
        "section": "product_profile",
        "question_number": 2,
        "question": "What disease(s) or conditions does your product treat/diagnose, and what is the incidence of prevalence of the disease/condition?",
        "question_type": "text",
        "options": None,
        "key_phases": """
Key Phrases [Lyme Disease]: 
    - Lyme Disease, 
    - Borrelia burgdorferi/B.burgdorferi
    - Stage 1/early localized, 
    - Stage 2/early disseminated, 
    - Stage 3/late disseminated
    - Deer tick disease
    - Post-treatment Lyme disease syndrome (PTLDS)
""",
    },
    {
        "section": "product_profile",
        "question_number": 3,
        "question": "What is the intended patient population?",
        "question_type": "text",
        "options": None,
        "key_phases": """
- Age
    - Pediatrics
        + Neonates (Birth to 28 days)
        + Infants (>28days to <2 years)
        + Children (>2 years to <12 years)
        + Adolescents (>12 years to <22 years)
    - Adults (aged 22 years and up)
- Sex
    - Male
    - Female
- Ethnicity
    - Hispanic or Latino
        + Mexican, Mexican American, Chicano
        + Puerto Rican
        + Cuban
        + Other Hispanic or Latino
    - Not Hispanic or Latino
- Race (minimum)
    - American Indian or Alaska Native
    - Asian
        + Asian Indian
        + Chinese
        + Filipino
        + Japanese
        + Korean
        + Vietnamese
        + Other Asian
    - Black or African American
    - Native Hawaiian or Other Pacific Islander
        + Guamanian or Chamorro
        + Samoan
        + Other Pacific Islander
    - White
- Socioeconomic Status
""",
    },
    {
        "section": "product_profile",
        "question_number": 4,
        "question": "Where is this product intended to be used?",
        "question_type": "text",
        "options": None,
        "key_phases": """
- Home Environment
    - Over-the-counter (OTC)
    - Non-professional use
    - Without clinical supervision
    - Self-monitoring/self-administered
    - For home use
    - No prescription required
    - Meets IEC 60601-1-11 (home healthcare environment) standards
- Clinical Environment
    - "Intended for use by trained healthcare professionals"
    - "For use in hospital or clinical settings"
    - "Requires professional supervision"
    - "Operated by licensed medical personnel"
    - "Designed for point-of-care use"
    - "For diagnostic/treatment use in clinical environments"
    - "Not intended for home use"
    - "Integrates with hospital systems/EHR"
    - "Prescription-use only (Rx only)"
    - "Requires physician authorization"
- Magnetic Resonance Environment
    - "MR Safe"
    - "MR Conditional"
    - "MR Compatible”
    - "Suitable for use in the MR environment"
    - "Tested in accordance with ASTM F2503"
    - "Non-ferromagnetic design"
    - "Can be safely used within the MRI suite"
    - "No known interactions with magnetic fields"
    - "Safe for use during MRI procedures"
    - "Does not interfere with MR imaging"
    - "Designed to minimize artifacts in MR images"
    - "Resistant to magnetic forces and torque"
    - "Constructed of non-magnetic materials"
- Transport (Ambulatory) Environment
    - "Intended for use in transport environments"
    - "Suitable for use in ambulances, helicopters, and mobile care units"
    - "Designed for pre-hospital or in-transit care"
    - "For use during patient transport"
    - "Optimized for emergency and transport settings"
    - "Compact and ruggedized for mobile use"
    - "Supports critical care during interfacility transport"
    - "Operates reliably in moving vehicles"
    - "Designed to withstand transport conditions (vibration, temperature, motion)"
    - "Meets IEC 60601-1-12 standards for emergency medical service environments"
""",
    },
    {
        "section": "product_profile",
        "question_number": 5,
        "question": "Is this product intended to be used in combination with a drug ,biological therapy, or other medical device?",
        "question_type": "text",
        "options": None,
        "key_phases": """
- Drug/Pharmaceutical
    - Therapeutic agent
    - Small molecule drug
    - Active pharmaceutical ingredient (API)
    - Analgesic (pain reliever)
    - Antibiotic
    - Antiviral
    - Antifungal
    - Antihypertensive
    - Antidepressant
    - Chemotherapy agent
    - Vaccine
    - Hormone therapy
    - Immunosuppressant
    - Monoclonal antibody (mAb)
    - Controlled substance
- Biologic
    - biological product
    - cellular/gene therapy
- Medical Device
    - Medical equipment
    - Diagnostic tool/device
    - Therapeutic device
    - Monitoring system
    - Assistive technology
    - Implantable device
    - Wearable medical device
- Combination Product
    - Combination product
    - Drug-device combination
    - Biologic-device combination
    - Integrated delivery system
    - Co-packaged product
    - Single-entity combination
    - Cross-labeled combination
    - Pre-filled delivery system
    - Fixed-dose combination
    - Dual-delivery mechanism
    - Targeted delivery system
    - Sustained-release platform
    - Implantable drug-eluting system
""",
    },
    {
        "section": "product_profile",
        "question_number": 6,
        "question": "Is the device life-supporting or life-sustaining?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """
- Life-sustaining device
- Life-supporting medical device
- Critical care device
- Essential for patient survival
- Used in life-threatening conditions
- Supports vital physiological functions
- Maintains essential organ function
- Required to sustain life in acute or chronic settings
- Indicated for use in patients requiring continuous physiological support
- Intended to support or sustain life
- Device failure could result in serious injury or death
""",
    },
    {
        "section": "product_profile",
        "question_number": 7,
        "question": "What is the specimen type?",
        "question_type": "radio",
        "options": [
            "Blood",
            "Serum",
            "Tissue",
            "Urine",
            "Saliva",
            "Other, please specify",
        ],
        "key_phases": """""",
    },
    {
        "section": "product_profile",
        "question_number": 8,
        "question": "Does the following apply to your device (check all that apply)",
        "question_type": "checkbox",
        "options": [
            "Laboratory Developed Test (LDT)",
            "Reprocessed Single Use Device",
            "Animal Derived Materials",
        ],
        "key_phases": """
- Laboratory Developed Test (LDT)
    - Developed and validated in-house
    - For use only at [Lab Name]
    - For clinical use in a single laboratory
    - Performed in a CLIA-certified laboratory
- Reprocessed Single Use Device
    - Reprocessed single-use device
    - "This device was originally intended for single use and has been reprocessed"
    - "Reprocessed in accordance with FDA requirements"
    - "Reprocessed and sterilized by [Reprocessor Name]"
    - "Reprocessed by an FDA-registered reprocessor"
    - "Third-party reprocessed" or "externally reprocessed"
    - "Originally labeled for single use"
    - "This device has been cleaned, tested, and sterilized for reuse"
    - "Meets FDA guidelines for reprocessed SUDs"
    - "Reprocessed under 21 CFR Part 820"
- Animal Derived Materials
    - "Processed to remove animal pathogens"
    - "Sterilized to eliminate potential viral or prion contamination"
    - "Compliant with FDA guidelines on animal-derived materials"
    - "Sourced from countries free of bovine spongiform encephalopathy (BSE)"
    - "Collagen from bovine/porcine source"
    - "of animal origin"
    - "Xenograft material" or "xenogenic tissue"
    - "Biologic scaffold derived from [animal species]"
    - "Animal-derived biocompatible material"
    - "Processed animal tissue"
""",
    },
    {
        "section": "performance_testing",
        "question_number": 9,
        "question": "Did you perform Precision (Repeatability/Reproducibility) study?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 10,
        "question": "Did you perform Linearity Study?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 11,
        "question": "Did you perform Analytical Sensitivity/Detection Limit(s) study?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 12,
        "question": "Did you have Assay Measuring Range information to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 13,
        "question": "Did you perform Assay Cut-off Study?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 14,
        "question": "Do you have Traceability Information to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 15,
        "question": "Do you have Stability information to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 16,
        "question": "Do you have Usability/Human Factors Studies specifically assessing the instructions and/or the device design in terms of impact to human behavior, abilities, limitations, and other characteristics on the ability of the device to perform as intended?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 17,
        "question": "Do you have other Analytical Performance Supportive Data to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 18,
        "question": "Did you perform Method comparison Study?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 19,
        "question": "Did you perform Matrix Comparison study?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 20,
        "question": "Do you have Clinical Sensitivity and/or Clinical Specificity to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 21,
        "question": "Do you have Clinical Cut-off information to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 22,
        "question": "Do you have other Clinical Supportive Data to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 23,
        "question": "Do you have Reference Range/Expected values information to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 24,
        "question": "Do you have clinical testing in this submission that includes patient-reported outcomes (PROs) or patient preference information?",
        "question_type": "checkbox",
        "options": [
            "Yes, PRO",
            "Yes, PPI",
            "Yes, PRO and PPI",
            "No",
        ],
        "key_phases": """
- PRO
    - Patient Reported Outcome
    - Self-report
    - self-completed questionnaires
    - self-completed subjective evaluation
    - Assessment of Pain levels
    - Assessment of Symptom severity
        + Functional Assessment of Chronic Illness Therapy—Fatigue scale
        + PROMIS Pain Interference measure
    - Assessment of health-related quality of Life
        + HRQL
        + Medical Outcomes Study Short Form SF-36
        + Sickness Impact Profile
        + health utility or preference measure
        + Neuro-QOL
        + PROMIS (Patient-Reported Outcomes Measurement Information System)
        + EQ-5D-5L
    - Assessment of Functional Status
        + Functional Status measure
        + physical function
- Upper Limb Functional Index
        + cognitive function
        + sexual function
    - Assessment of Health Behaviors
        + Health risk assessments (HRAs)
        + Behavioral Risk Factor Surveillance System (BRFSS)
        + National Health and Nutrition Examination Survey (NHANES)
        + CAGE-Adapted to Include Drugs (CAGE-AID)
        + School Health Action, Planning and Evaluation System (SHAPES)
        + Morisky Medication Adherence Scale  
    - Satisfaction with Care
        + patient satisfaction
- concerns about the disease and its treatment
- issues of treatment affordability and financial burden for the patient
- communication with health care providers
- access to services
- satisfaction with treatment explanations
- confidence in the physician
        + patient motivation and activation
- Patient Activation Measure (PAM)
        + patient reports of their actual experiences
- Consumer Assessment of Healthcare Providers and Systems (CAHPS)
- PPI
    - Treatment preferences
        + Choice of medication
        + Choice of hospital or outpatient care
        + Degree of treatment intensity
    - Outcome preferences
        + Symptom relief vs complete treatment
        + Preventions of complications
        + Length of Life
    - Preferences for Aspects of care
    - Situation of care: Patient's understanding of their clinical status, treatment requirements, and care pathway
    - Expectations of care: Based on the patient's preference for contact, previous care, psychological status, and perceived requirements
    - Demands on the patient: Patient's social situation and choice consequences
    - Care resources allocation capacity: Financial, social, healthcare, and infrastructural resources
""",
    },
    {
        "section": "performance_testing",
        "question_number": 25,
        "question": "Please identify the attachment(s) and page number(s) of any information provided related to patient-reported outcomes (PROs) for this section, such as the PRO questionnaire, dossier, and/or other supportive documents.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 26,
        "question": "Please identify the attachment(s) and page number(s) of any information provided related to patient preference information (PPI) for this section, such as the PPI survey, protocol, attribute table, and/or other supportive documents as appropriate.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 27,
        "question": "Is one or more of the included clinical investigations intended to support this submission subject to the requirements governing FDA acceptance of data from clinical investigations?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 28,
        "question": "Where the supporting clinical investigations included in this submission conducted?",
        "question_type": "radio",
        "options": [
            "All clinical investigations were conducted solely inside the US",
            "All clinical investigations were conducted solely outside the US",
            "Clinical Investigations were conducted at both US and OUS sites",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 29,
        "question": "Do you have Animal Testing to include in this submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 30,
        "question": "Please include a study protocol which includes all elements as outlined in 21 CFR 58.120.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 31,
        "question": "Please include a final study report which includes all elements as outlined in 21CFR 58.185.",
        "question_type": "text",
        "options": None,
        "key_phases": """
(1)	a statement that the study was conducted in compliance with applicable requirements in the GLP regulation (21 CFR Part 58), 
(2)	or, if the study was not conducted in compliance with the GLP regulation, prompt the user to please explain why the noncompliance would not impact the validity of the study data provided to support this submission.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 32,
        "question": "Provide the predicate device submission number (e.g., K180001) that is the best comparator for the testing attached.",
        "question_type": "text",
        "options": None,
        "key_phases": """
Based on the attached report, AI should provide reference to the predicate device that most closely resembles the provided report data.
AI should summarize the Electrical, Mechanical and Thermal Safety Testing of the device, or prompt the user to justify why testing was not needed.""",
    },
    {
        "section": "performance_testing",
        "question_number": 33,
        "question": "Is the device electrical (battery or mains powered)?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 34,
        "question": "How many devices/accessories/components were subjected to EMC testing (max 4)?",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 35,
        "question": "Please select the most severe harm that could be caused to the patient, user, or operator as a result of potential malfunction, disruption, or degradation due to electromagnetic interference (EMI).",
        "question_type": "radio",
        "options": [
            "Death or Serious Injuries",
            "Non-Serious Adverse Events",
            "No Reported or Potential Harm",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 36,
        "question": "Was testing performed according to a recognized edition of IEC 60601-1-2 or IEC 61326-2-6 and, if so, was an ASCA test summary report provided",
        "question_type": "radio",
        "options": [
            "Yes, 60601-1-2 without ASCA",
            "Yes, 60601-1-2 with ASCA",
            "Yes, 61326-2-6",
            "No",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 37,
        "question": "If the device under test is not the final finished version, please provide a justification for why the differences don't affect EMC. If the device under test is the final finished version, please state this",
        "question_type": "text",
        "options": None,
        "key_phases": """
AI Should prompt the user to confirm that the testing was completed on the final finished version of the device. If not, prompt the user to provide justification for why the differences don't affect EMC.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 38,
        "question": "Please list the Essential Performance Characteristics that are specific to the device, or provide a rationale why the device has no Essential Performance.",
        "question_type": "text",
        "options": None,
        "key_phases": """
AI should parse out the Essential Performance Characteristics. This will generally be a dedicated section in the report, so “Essential Performance” should be enough of a key phrase.
If the report states something like, “not applicable”, or “No Essential Performance”, then the AI should prompt the user to justify why the device has no Essential Performance.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 39,
        "question": "Please provide specific page number(s) in the summary/report that include pass/fail criteria specific to the device that are based on device functions, intended use, and Essential Performance. It is recommended that all device functions that are associated with basic safety or Essential Performance be tested and include device-specific pass/fail criteria.",
        "question_type": "text",
        "options": None,
        "key_phases": """
Key Phrases:
- Pass/Fail Criteria
- Acceptance Criteria
- Performance Criteria
""",
    },
    {
        "section": "performance_testing",
        "question_number": 40,
        "question": "If wireless technology is used in the medical device to achieve its intended use, was it “on” and communicating with other medical device subsystems or ancillary equipment during EMC",
        "question_type": "radio",
        "options": [
            "Yes",
            "No",
            "Inapplicable",
        ],
        "key_phases": """
- RFID
- Wifi
- Bluetooth
- ZigBee
- Cellular
""",
    },
    {
        "section": "performance_testing",
        "question_number": 41,
        "question": "If the device includes any smart batteries that can be removed from the device for recharging, were the batteries tested as a standalone component during ESD testing?",
        "question_type": "radio",
        "options": [
            "Yes",
            "No",
            "Inapplicable",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 42,
        "question": "If there were any degradations or observations noted during the testing, describe how the device(s) continued to meet the device-specific pass/fail criteria during these degradations or observations.",
        "question_type": "text",
        "options": None,
        "key_phases": """
- Phenomena
- Observation/Observed
- Damage
- Degradation
- Fail/Failures
""",
    },
    {
        "section": "performance_testing",
        "question_number": 43,
        "question": "If any of the referenced standard's allowances were used during the testing (e.g. lowered ESD immunity), please provide these below.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 44,
        "question": "If there were any deviations from the referenced standard, please describe these below.",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should be able to provide examples to the user of the referenced standards allowances, then prompt the user to provide the allowances used and their justification.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 45,
        "question": "Please add an attachment that includes descriptions of all modifications, as well as a statement indicating that all changes or modifications will be incorporated in the device intended for marketing. Not providing an attachment indicates no modifications were made in order to pass any of the EMC tests. In addition, be sure you include an adequate assessment of whether these modifications might impact other aspects of the device (e.g., performance, biocompatibility). It is recommended that the attachment contain information to demonstrate that the modifications would have no impact on the other aspects or that the modified device was used for the other performance tests.",
        "question_type": "text",
        "options": None,
        "key_phases": """
Have an area for potential attachment. If the user does not provide attachment, provide the user with a warning that states “Not providing an attachment indicates no modifications were made in order to pass any of the EMC tests” and ensure that they confirm no attachment]
If attachment is provided, the AI should parse the document for references to other sections, and prompt the user to justify any impact to other sections identified.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 46,
        "question": "Please add an attachment that addresses the risks associated with exposure to specific EM emitters that are not adequately addressed by IEC 60601-1-2 (risk analysis with appropriate mitigation that might include testing or labeling) foreseeable in the intended use vicinity (e.g., RFID, security systems such as metal detectors and EAS, diathermy, electrocautery, MRI, electrosurgical units)",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 47,
        "question": "How many separate wireless functions are there (max 5). For each device/accessory listed in the question above, the following data should be parsed:",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 48,
        "question": "Specify the device function to be implemented wirelessly and risks associated with failure, disruption, or delay of communication. Please consider inherent risks due to complete wireless communication loss as well as risks identified by the sponsor during their risk analysis process. Additionally, please consider the safeguards and redundancies that might be built into the wireless function when considering the risk.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 49,
        "question": "Please choose the most appropriate choice for the risk of the wireless function (which may not be the same as the risk of the device). The risks of the wireless function are defined in AAMI TIR69.",
        "question_type": "radio",
        "options": [
            "Negligible",
            "Minor (Tier 3)",
            "Moderate (Tier 2)",
            "Major (Tier 1)",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 50,
        "question": "What is the Quality of Service (QoS) of the device?",
        "question_type": "text",
        "options": None,
        "key_phases": """
- Accessibility/signal priorities
    - “Consistent wireless signal”
    - “Stable connection without dropout”
    - “Strong signal reception in clinical environment”
    - “Interference-free transmission”
- Latency
    - “Low-latency communication”
    - “Real-time data transmission”
    - “Minimal delay in telemetry updates”
    - “Near-instantaneous response time”
- Throughput
    - “Sufficient bandwidth for continuous monitoring”
    - “Capable of handling high data volume”
    - “No bottleneck during simultaneous device usage”
    - “High data throughput in busy environments”
- Data Integrity
    - “Low packet error rate”
    - “Error correction protocol in place”
    - “No significant packet loss during transmission”
    - “Retransmission mechanism for lost data”
    - “Encrypted wireless transmission”
    - “Authenticated device communication”
    - “HIPAA-compliant data handling”
    - “Secure pairing with hospital network”
    - “High availability (>99.9%)”
    - “Failover mechanism in case of disconnection”
    - “Redundant wireless path”
    - “No loss of critical data packets”
""",
    },
    {
        "section": "performance_testing",
        "question_number": 51,
        "question": "Please select all the technologies that apply to this wireless function.",
        "question_type": "radio",
        "options": [
            "Bluetooth",
            "Wifi",
            "Zigbee",
            "RFID",
            "Cellular",
            "Other",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 52,
        "question": "What is the intended range when using RFID to implement the wireless function?",
        "question_type": "radio",
        "options": [
            "Short Range (less than 6 inches)",
            "Long Range",
        ],
        "key_phases": """
- “Read range of up to X meters/feet”
- “Typical operating range: X to Y meters”
- “Designed for short-range identification”
- “Long-range detection capability”
""",
    },
    {
        "section": "performance_testing",
        "question_number": 53,
        "question": "Did you address mitigations to poor or no cellular network coverage, and managing the subscription to cellular network access?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 54,
        "question": "Attach the Wireless Coexistence Testing Protocol/Report",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 55,
        "question": "Please describe the Functional Wireless Performance (FWP).",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should generate a summary of the FWP Results and Conclusions.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 56,
        "question": "Please describe the pass/fail criteria for the FWP and be sure to clarify how each criterion was quantified and measured.",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should parse the pass/fail criteria, and prompt the user to clarify how each criterion was quantified and measured.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 57,
        "question": "Was the coexistence testing conducted to Tier X (per the risk category chosen above)?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 58,
        "question": "Were the Equipment Under Test (EUT) and its companion device both exposed to the unintended signal?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 59,
        "question": "Was the functional wireless performance (FWP) maintained during the testing? If not, were adequate mitigations provided?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 60,
        "question": "Does this product contain software elements?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """
- Cloud Communication
    - Cloud-based technology
    - Cloud-enabled functionality
    - Secure cloud data transmission
    - Real-time cloud communication
    - Cloud-based monitoring platform
    - Device-to-cloud (D2C) architecture
    - Remote data sync via cloud
    - Cloud-integrated device interface
    - Integrates with cloud-based EMR/EHR systems
- Network connection
    -  Supports local area network (LAN) or wide area network (WAN) communication
    - Transmits data over secure network channels
    - Enables device communication via network infrastructure
    - Seamlessly integrates with hospital or clinic networks
    - Uses Ethernet, Wi-Fi, or cellular networks for data exchange
    - Offers network-based diagnostics and updates
    - Automatically synchronizes with remote servers over the network
    - Supports peer-to-peer or client-server communication via network
- Wireless communication
    - Wireless data transmission
    - Wireless communication capabilities
    - Supports [Bluetooth/Wi-Fi/NFC/Cellular] connectivity
    - Short-range/long-range wireless connectivity
- USB/serial ports/removeable media
    - Allows offline data backup via removable media
    - Facilitates secure data transfer through external drives
    - Supports patient data export/import using USB or SD storage
    - Convenient file transfer via removable media
    - Local data archiving through external memory support
- Software upgrades
""",
    },
    {
        "section": "performance_testing",
        "question_number": 61,
        "question": "Does the device contain digital health technology?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 62,
        "question": "Please select the Documentation Level based on the device's intended use, the design of the device, and the risks of the device software function(s) in the context of the device's intended use.",
        "question_type": "radio",
        "options": [
            "Basic Documentation",
            "Enhanced Documentation",
        ],
        "key_phases": """
[Brittany to provide an example of Documentation Level Evaluation]
[Software Documentation]
- Software/Firmware Description
- Risk Management File (including Hazard Analysis)
- Software Requirements Specifications (SRS)
- System and Software Architecture Design (SAD) Chart
- Software Design Specifications (SDS) - [ONLY NEEDED IF ENHANCED DOCUMENTATION IS SELECTED]
- Software Life Cycle Process Description/Software Development, Configuration Management, and Maintenance Practices
- Software Testing as Part of Verification & Validation
- Software Version/Revision Level History
- Unresolved Software Anomalies
[Cybersecurity]
""",
    },
    {
        "section": "performance_testing",
        "question_number": 63,
        "question": "Please attach your security risk management report detailing a separate, parallel, and interconnected security risk management process. This is different from your safety risk management process.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 64,
        "question": "Please attach your threat model addressing all the end-to-end elements of the system.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 65,
        "question": "List the Threat Methodology (e.g. STRIDE, Attack Trees, Kill Chain, DREAD) that you used.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 66,
        "question": "Does the threat model documentation include Architecture Views (Global System View, Multi-Patient Harm View, Updateability/Patchability View, and Security Use Case Views)?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 67,
        "question": "Please attach your Cybersecurity Risk Assessment",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should cite the page number(s) of the cybersecurity risk assessment where the methodology and acceptance criteria are described.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 68,
        "question": "Does the Cybersecurity Risk Assessment avoid using probabilities for the likelihood assessment and use exploitability instead?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 69,
        "question": "Please attach your Software Bill of Materials (SBOM).",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 70,
        "question": "Please attach a document to provide the software level of support and end-of support date for each software component (e.g. OTS software) identified in the SBOM. For any component where this information was not available, provide a justification.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 71,
        "question": 'List the supported operating system(s) and associated version(s) your device(s)/system uses. Be aware that if you list any operating systems that are no longer supported (e.g. Windows 7, Mac OS 9) or nearing end of support, this will generally be considered an inaccurate response. Type "N/A" if your device(s) does not use an operating system.',
        "question_type": "text",
        "options": None,
        "key_phases": """
- Operating System
- “Runs on Windows Embedded Standard 7”
- “Powered by Linux kernel version X.X”
- “Android-based interface for user interaction”
- “Utilizes RTOS such as FreeRTOS / VxWorks / QNX”
- “iOS integration for companion mobile apps”
- “Ubuntu Core for secure IoT operation”
- “Yocto Linux build customized for embedded use”
""",
    },
    {
        "section": "performance_testing",
        "question_number": 72,
        "question": "Please attach a safety and security assessment of cybersecurity vulnerabilities in the component software used by the device for all software components in the SBOM and a description of any controls that address the vulnerability.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 73,
        "question": "Please attach an assessment of any unresolved anomalies for cybersecurity impact. If none exist, attach a document stating that no unresolved anomalies exist.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 74,
        "question": "Please attach data from monitoring cybersecurity metrics. If metric data are unavailable, please attach a justification.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 75,
        "question": "Please attach information on the security controls categories included in the device.",
        "question_type": "text",
        "options": None,
        "key_phases": """
AI should parse the following page numbers from this attachment for the references below:
- A) Authentication controls: 
- B) Authorization controls: 
- C) Cryptography controls: 
- D) Code, data, and execution integrity controls: 
- E) Confidentiality controls: 
- F) Event detection and logging controls: 
- G) Resiliency and recovery controls: 
- H) Firmware and software update controls:
""",
    },
    {
        "section": "performance_testing",
        "question_number": 76,
        "question": "Please attach a document(s) that contains a Global System View, Multi-Patient Harm View, Updatability/Patchability View, and Security Use Case Views. ",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should prompt the user if attachment is not added to justify why testing was not performed.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 77,
        "question": "Please attach a document(s) that describes the cybersecurity testing performed and the associated test reports.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 78,
        "question": "Please attach a Cybersecurity Management Plan.",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should cite the page numbers of the following references:
- Post market updates and patches to device and related systems to address vulnerabilities with controlled risks (i.e. sufficiently low (acceptable) residual risk of patient harm due to the vulnerability), provide a description and justification for the timeline to make updates and patches on a regularly scheduled deployment cycle.
- Post market updates and patches to device and related systems to address vulnerabilities with uncontrolled risks (i.e. unacceptable residual risk of patient harm due to inadequate compensating controls and risk mitigations), provide a description and justification for the timeline to make updates and patches as soon as possible out of cycle.  
- a description of and justification for the time-lines to make patches on a regular cycle and out of cycle.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 79,
        "question": "How many Electronic interfaces are there (max 20)?",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 80,
        "question": "What is the name of the electronic interface?",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 81,
        "question": "Is the electronic interface inactive (i.e. not meant to connect, exchange, or use data with or from other medical devices, products, technologies, or systems)?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 82,
        "question": "Are the interfaces only meant for service or maintenance?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 83,
        "question": "Is the data flow only meant for transferring, storing, converting formats, or displaying clinical laboratory test and not intended to interpret or analyze clinical laboratory test or other device data, results, and findings?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 84,
        "question": "Describe the Electronic Interface.",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should prompt the user to describe the electronic interface (i.e., smartphone, device monitor, etc.)
""",
    },
    {
        "section": "performance_testing",
        "question_number": 85,
        "question": "Attach the Interoperability Risk Assessment / Verification and Validation",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 86,
        "question": "Are there any direct or indirect tissue contacting components (i.e. does any part come in contact with a patient)?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """
- Direct/indirect contact
- Nature of contact
- Frequency/duration of contact
    - Prolonged contact
    - Permanent contact
- Implant/Implantation
""",
    },
    {
        "section": "performance_testing",
        "question_number": 87,
        "question": "Is the device or a component implanted?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """
- Implant/Implantation
- “Implanted within the body”
- “Surgically implanted device”
- “Device remains in situ”
- “Long-term implantation”
- “Implantation via catheter/surgical incision”
- “Subcutaneous insertion”
- “Percutaneously implanted”
""",
    },
    {
        "section": "performance_testing",
        "question_number": 88,
        "question": "How many tissue contacting products/components/materials are there (max 50)?",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 89,
        "question": "Identify the tissue contacting device/accessory/component.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 90,
        "question": "Please list the exact names and any identifiable information for the material(s) used.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 91,
        "question": "If color additives are included, please list, or state N/A.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 92,
        "question": "Choose the intended contact of the particular material.",
        "question_type": "radio",
        "options": [
            "Direct",
            "Indirect",
            "Both",
        ],
        "key_phases": """
- Direct
    - “Direct contact with patient tissue”
    - “Device touches internal organs”
    - “Invasive interface with tissue or blood”
    - “Contacts mucosal surfaces”
    - “Skin-penetrating component”
    - “Implanted into living tissue”
    - “Intravaginal/intraoral/intranasal device”
    - “Delivers energy to tissue”
    - “Monitors electrical activity from skin surface”
    - “Administers drug through mucosal membrane”
    - “Penetrates the epidermis”
    - “Positioned inside body cavity”
- Indirect
    - “Contacts intact skin only”
    - “Used on skin surface without penetration”
    - “No direct tissue contact”
    - “Proximal to tissue without contact”
    - “External application over anatomical site”
    - “Remote sensing through clothing”
    - “Optical scanning without contact”
    - “Non-contact thermography”
    - “Near-field monitoring without touching skin”
""",
    },
    {
        "section": "performance_testing",
        "question_number": 93,
        "question": "Are the listed components in contact with intact skin only AND are all the component materials included in Attachment G, Section B of the FDA Biocompatibility Guidance?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 94,
        "question": "Is there a potential for repeat exposure?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 95,
        "question": "Choose the type of tissue contact of your materials listed.",
        "question_type": "radio",
        "options": [
            "Surface Device: Skin",
            "Surface Device: Mucosal Membrane",
            "Surface Device: Breached or Compromised Surfaces",
            "External Communicating Device: Blood Path, Indirect",
            "External Communicating Device: Tissue/Bone/Dentin",
            "External Communicating Device: Circulating Blood",
            "Implant Device: Tissue/Bone",
            "Implant Device: Blood",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 96,
        "question": "What is the duration of exposure/contact?",
        "question_type": "radio",
        "options": [
            "Less than 24 hours (includes transient contact)",
            "24 hours to 30 days",
            "Greater than 30 days (i.e. permanent)",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 97,
        "question": "Please attach any documentation (e.g., test reports) pertaining to the biocompatibility of your device. ",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 98,
        "question": "Is the device or a component packaged as sterile?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """
- Sterile/sterilization
- “Sterile until opened or damaged”
- “Single-use, sterile packaging”
- “Do not resterilize”
- “Sterile barrier system intact”
- “Sterilization cycle monitored using biological indicators”
- Used in sterile surgical field” (typically requires terminal sterilization)
- “Pre-sterilized and ready to use”
- “Sterilized prior to clinical use”
- “Delivered sterile for implantable application”
- “End-user sterilization required”
- “Sterility assurance level (SAL) of 10⁻⁶”
- “Terminally sterilized before packaging”
- “Meets FDA requirements for terminal sterilization”
- “Sterilization validated per ANSI/AAMI standards
""",
    },
    {
        "section": "performance_testing",
        "question_number": 99,
        "question": "How many sterilization methods are there (max 4)?",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 100,
        "question": "Identify the device(s) / accessory(ies) / component(s) that is sterilized.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 101,
        "question": "What is the Sterilization Method?",
        "question_type": "text",
        "options": [
            "Steam (Moist Heat) (Est A)",
            "Ethylene Oxide (EO,EtO) (Est A)",
            "Radiation (Est A)",
            "Dry Heat (Est A)",
            "Hydrogen Peroxide (Est A)",
            "Ozone (Est B)",
            "Flexible Bag System (Est B)",
            "Novel Method",
        ],
        "key_phases": """
- Steam
    - “Exposed to 121°C for X minutes”
    - “Steam sterilization via autoclave”
    - “Validated for multiple autoclave cycles”
    - “Sterilized by moist heat”
    - “Autoclaved at 134°C for 4 minutes”
    - “Steam cycle applied before packaging”
    - “Compatible with high-pressure steam sterilization”
    - “Validated per ISO 17665”
    - “Resterilizable via autoclaving”
- Ethylene Oxide
    - “Sterilized using ethylene oxide (EtO)”
    - “EtO cycle parameters: temperature, humidity, gas concentration”
    - “Conforms to ISO 11135 for EtO sterilization”
    - “Packaged for EtO sterilization compatibility”
    - “Designed for EtO sterilization due to heat sensitivity”
    - “Sterilized using ethylene oxide gas”
    - “Subjected to EtO cycle”
    - “Low-temperature gas sterilization method”
    - “Requires aeration after EtO exposure”
- Radiation
    - “Gamma sterilized”
    - “Sterilized by electron beam (e-beam)”
    - “Radiation sterilized”
    - “Validated per ISO 11137 for radiation sterilization”
    - “Double-pouched for gamma compatibility”
    - “Irradiation dose: 25 kGy”
    - “Gamma-stable polymers used”
    - “Gamma irradiated at 25-40 kGy”
    - “Exposed to cobalt-60 radiation”
    - “Sterilized via gamma rays”
    - “Radiation dose confirmed by dosimeter”
    - “Compatible with gamma sterilization”
    - “Electron beam sterilization process”
    - “E-beam treated medical device”
    - “Accelerated electrons used for sterilization”
    - “Irradiated with high-energy beam”
    - “Short exposure sterilization
- Dry Heat
    - “Dry heat sterilization method”
    - “Exposed to 160°C for 2 hours”
    - “Sterilized by dry heat oven”
    - “Validated for dry heat sterilization”
    - “High-temperature resistant components used”

- Hydrogen Peroxide
    - “Hydrogen peroxide plasma sterilization”
    - “Plasma chamber sterilization”
    - “Sterilized using hydrogen peroxide plasma”
    - “Vaporized hydrogen peroxide (VHP) process”
    - “Low-temperature plasma sterilization”
    - “Compatible with STERRAD system”
    - “Safe for heat-sensitive electronics”
""",
    },
    {
        "section": "performance_testing",
        "question_number": 102,
        "question": "What is the dose?",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should parse the radiation dose (should be in units of kGy)
""",
    },
    {
        "section": "performance_testing",
        "question_number": 103,
        "question": "What standard(s) were used for validation?",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should parse this from the attached sterility validation reports.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 104,
        "question": "What are the maximum levels of sterilant residuals that remain on the device, and what is your explanation for why those levels are acceptable for the device type and the expected duration of patient contact?",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should parse the maximum residual levels from the provided sterility validation, and then prompt the user to justify their acceptablity.
""",
    },
    {
        "section": "performance_testing",
        "question_number": 105,
        "question": "What validation method was used for the sterilization cycle?",
        "question_type": "radio",
        "options": [
            "Overkill Approach (e.g Half-Cycle method)",
            "(Combined) Biological Indicator/Bioburden Approach",
            "(Absolute) Bioburden Approach (e.g Natural Bioburden method)",
            "Other",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 106,
        "question": "What validation method was used for the sterilization cycle?",
        "question_type": "radio",
        "options": [
            "Dose setting using Bioburden",
            "Dose setting using Fraction Positive Information",
            "VDmax25 (for 25kGy dose)",
            "VDmax15 (for 15kGy dose)",
            "(Absolute) Bioburden Approach (e.g. Natural Bioburden method)",
            "Other",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 107,
        "question": "What is the Sterility Assurance Level (SAL)?",
        "question_type": "radio",
        "options": [
            "1e-6",
            "1e-3",
            "Other",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 108,
        "question": 'If a device within the submission should be "Non- Pyrogenic," or if you are asserting a device is "Non-Pyrogenic," what is the pyrogenicity test method?',
        "question_type": "radio",
        "options": [
            "LAL and Rabbit Pyrogen Test",
            "Other",
            "Not labeled nor required to be “Non-Pyrogenic”",
        ],
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 109,
        "question": "Please provide a description of the packaging, the materials used, and a description of the package test methods.",
        "question_type": "text",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 110,
        "question": "Has the device/components been previously assessed for shelf-life (accelerated aging, etc.)",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
    {
        "section": "performance_testing",
        "question_number": 111,
        "question": "If yes, what is the proposed shelf-life?",
        "question_type": "text",
        "options": None,
        "key_phases": """
Should parse from the shelf-life (accelerated aging) testing report.
Should analyse attachment and provide summary of the methods used to support the sterility and performance of the device over its proposed shelf-life. If no attachment is provided, AI should prompt the user to provide a rationale for why testing to establish shelf-life is not applicable.
""",
    },
    {
        "section": "claims_builder",
        "question_number": 112,
        "question": "What is the Magnetic Resonance (MR) safety status for the device(s) in the submission?",
        "question_type": "radio",
        "options": [
            "MR Safe",
            "MR Unsafe",
            "MR Conditional",
            "Not Evaluated",
        ],
        "key_phases": """""",
    },
    {
        "section": "claims_builder",
        "question_number": 113,
        "question": "Is literature referenced in the submission?",
        "question_type": "boolean",
        "options": None,
        "key_phases": """""",
    },
]
