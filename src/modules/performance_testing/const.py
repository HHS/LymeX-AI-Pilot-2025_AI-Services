# mapping: {section_key → {canonical_test_code : human-readable label}}
TEST_CATALOGUE: dict[str, dict[str, str]] = {
    "analytical": {
        "precision":          "Precision (Repeatability / Reproducibility)",
        "linearity":          "Linearity",
        "sensitivity":        "Analytical Sensitivity / Detection Limit(s)",
        "measuring_range":    "Assay Measuring Range",
        "cut_off":            "Assay Cut-off",
        "traceability":       "Traceability",
        "stability":          "Stability",
        "usability":          "Usability / Human-Factors",
        "other_analytical":   "Other Analytical supportive data",
    },
    "comparison": {
        "method":             "Method Comparison",
        "matrix":             "Matrix Comparison",
    },
    "clinical": {
        "clin_sens_spec":     "Clinical Sensitivity / Specificity",
        "clin_cut_off":       "Clinical Cut-off",
        "other_clinical":     "Other Clinical supportive data",
    },
    "animal_testing": {
        "glp_animal":         "GLP-compliant Animal Testing",
    },
    "emc_safety": {
        "iec_60601_1_2":      "EMC (IEC 60601-1-2 / IEC 61326-2-6)",
        "asca_summary":       "ASCA Test Summary Report",
        "design_mods":        "Design-modifications-to-pass report",
        "rf_risk_analysis":   "EM emitter risk analysis (RFID, 5 G, …)",
    },
    "wireless": {
        "coexistence":        "Wireless Coexistence / FWP",
    },
    "software": {
        "sw_description":     "Software / Firmware Description",
        "risk_file":          "Risk-management File",
        "srs":                "Software Requirements Spec",
        "arch_view":          "Architecture Diagram",
        "sds":                "Software Design Spec",
        "lifecycle_desc":     "Lifecycle / Config mgmt",
        "vnv_reports":        "V&V Reports",
        "revision_history":   "Revision History",
        "unresolved_anom":    "Unresolved Anomalies List",
    },
    "cybersecurity": {
        "security_rm_report": "Security Risk-Management Report",
        "threat_model":       "Threat Model Document",
        "cyber_risk":         "Cybersecurity Risk Assessment",
        "sbom":               "SBOM",
        "component_eos":      "End-of-Support Statement",
        "vuln_assessment":    "Vulnerability Assessment",
        "anom_impact":        "Anomaly Impact Assessment",
        "metrics":            "Security Metrics Monitoring",
        "controls":           "Security Controls Categories",
        "arch_views":         "Security Architecture Views",
        "test_reports":       "Cybersecurity Testing Reports",
        "cyber_mgmt_plan":    "Cybersecurity Management Plan",
    },
    "interoperability": {
        "interop_docs":       "Interoperability V&V / Risk docs",
    },
    "biocompatibility": {
        "biocomp_tests":      "Biocompatibility test reports",
        "biocomp_rationale":  "Biocomp rationale (if no testing)",
    },
    "sterility": {
        "steril_validation":  "Sterilization Validation",
        "pkg_description":    "Packaging Description & Tests",
        "shelf_life":         "Shelf-life / Aging Report",
        "pyrogenicity":       "Pyrogenicity Test",
    },
    "labeling": {
        "packaging_labels":   "Packaging Artwork",
        "ifu":                "IFU / Directions for Use",
        "extra_labeling":     "Additional labeling pieces",
        "symbols_glossary":   "Symbols glossary",
    },
    "literature": {
        "references":         "Literature Reference PDFs",
    },
}