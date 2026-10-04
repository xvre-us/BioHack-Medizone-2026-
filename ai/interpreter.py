"""Evidence-grounded interpretation layer for Mystery Gene Decoder."""

from typing import Any, Dict, List


def interpret_findings(findings: Dict[str, Any]) -> Dict[str, Any]:
    """Convert structured bioinformatics findings into a safe explanation."""

    sequence_length = findings.get("sequence_length")
    similarity = findings.get("similarity")
    conserved_regions = findings.get("conserved_regions", [])
    variable_positions = findings.get("variable_positions", [])
    annotations = findings.get("annotations", [])

    observations: List[str] = []

    if sequence_length is not None:
        observations.append(
            f"The analyzed sequence is {sequence_length} bp long."
        )

    if similarity is not None:
        observations.append(
            f"The reported similarity is {similarity:.1%} "
            "within the supplied comparison set."
        )

    if conserved_regions:
        observations.append(
            f"{len(conserved_regions)} conserved region(s) were reported."
        )

    if variable_positions:
        observations.append(
            f"{len(variable_positions)} variable position(s) were reported."
        )

    evidence = []

    for annotation in annotations:
        evidence.append({
            "source": annotation.get("source", "Unknown source"),
            "claim": (
                annotation.get("description")
                or annotation.get("label", "Unspecified annotation")
            )
        })

    limitations = [
        "These findings alone do not establish the biological function of the gene.",
        "Sequence similarity should not be treated as proof of functional equivalence.",
        "This interpretation is limited to the evidence supplied by the analysis pipeline."
    ]

    next_investigations = [
        "Check conserved regions against trusted annotation or domain databases.",
        "Investigate whether variable positions overlap known functional regions.",
        "Review the provenance and quality of the sequence-similarity evidence."
    ]

    confidence = (
        "moderate"
        if similarity is not None and evidence
        else "low"
    )

    return {
        "what_am_i_seeing": (
            " ".join(observations)
            or "No interpretable findings were supplied."
        ),
        "why_it_might_matter": (
            "The reported similarity and conserved regions may provide "
            "useful clues for further investigation, but they do not by "
            "themselves establish gene function."
        ),
        "next_investigations": next_investigations,
        "evidence": evidence,
        "limitations": limitations,
        "confidence": confidence
    }


if __name__ == "__main__":
    import json
    from pathlib import Path

    input_path = Path(__file__).with_name("mock_input.json")
    findings = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    print(
        json.dumps(
            interpret_findings(findings),
            indent=2
        )
  )
