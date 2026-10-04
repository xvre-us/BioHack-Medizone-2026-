def normalize_findings(raw_findings):
    return {
        "sequence_id": raw_findings.get("sequence_id"),
        "sequence_length": raw_findings.get("sequence_length"),
        "confidence_signals": raw_findings.get(
            "confidence_signals", {}
        ),
        "plm_findings": raw_findings.get(
            "plm_findings", {}
        ),
        "conserved_regions": raw_findings.get(
            "conserved_regions", []
        ),
        "variable_positions": raw_findings.get(
            "variable_positions", []
        ),
        "annotations": raw_findings.get(
            "annotations", []
        ),
    }
