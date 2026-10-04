def normalize_findings(raw_findings):
    return {
        "sequence_length": raw_findings.get("sequence_length"),
        "similarity": raw_findings.get("similarity"),
        "conserved_regions": raw_findings.get("conserved_regions", []),
        "variable_positions": raw_findings.get("variable_positions", []),
        "annotations": raw_findings.get("annotations", []),
    }
