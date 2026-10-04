"""Evidence-grounded interpretation layer for Mystery Gene Decoder."""

from typing import Any, Dict, List


def interpret_findings(findings: Dict[str, Any]) -> Dict[str, Any]:
    """Convert structured PLM/bioinformatics findings into a safe explanation."""

    sequence_length = findings.get("sequence_length")

    confidence_signals = findings.get("confidence_signals", {})
    latent_similarity = confidence_signals.get("latent_similarity_score")
    classification_margin = confidence_signals.get("classification_margin")

    plm_findings = findings.get("plm_findings", {})
    predicted_category = plm_findings.get("predicted_functional_category")
    top_predictions = plm_findings.get("top_predictions", [])
    nearest_clusters = plm_findings.get("nearest_latent_clusters", [])
    latent_distance = plm_findings.get("latent_distance")

    conserved_regions = findings.get("conserved_regions", [])
    variable_positions = findings.get("variable_positions", [])
    annotations = findings.get("annotations", [])

    # ---------------------------------------------------------
    # 1. What are we seeing?
    # ---------------------------------------------------------

    observations: List[str] = []

    if sequence_length is not None:
        observations.append(
            f"The analyzed sequence is {sequence_length} residues long."
        )

    if predicted_category:
        observations.append(
            f"The PLM analysis places the sequence in the "
            f"'{predicted_category}' functional category."
        )

    if top_predictions:
        top_prediction = top_predictions[0]
        label = top_prediction.get("label")
        probability = top_prediction.get("probability")

        if label and probability is not None:
            observations.append(
                f"The top model prediction is '{label}' "
                f"with a reported probability of {probability:.1%}."
            )

    if nearest_clusters:
        clusters = ", ".join(nearest_clusters)
        observations.append(
            f"The sequence is closest in latent space to: {clusters}."
        )

    if conserved_regions:
        observations.append(
            f"{len(conserved_regions)} conserved region(s) were reported."
        )

    if variable_positions:
        observations.append(
            f"{len(variable_positions)} variable position(s) were reported."
        )

    # ---------------------------------------------------------
    # 2. Evidence
    # ---------------------------------------------------------

    evidence: List[Dict[str, str]] = []

    for annotation in annotations:
        source = annotation.get("source", "Unknown source")
        description = (
            annotation.get("description")
            or annotation.get("label")
            or "Unspecified annotation"
        )

        evidence.append(
            {
                "source": source,
                "claim": description,
            }
        )

    # Add PLM confidence signals as computational evidence.
    if latent_similarity is not None:
        evidence.append(
            {
                "source": "PLM latent similarity",
                "claim": (
                    f"Latent similarity score = {latent_similarity:.4f}"
                ),
            }
        )

    if classification_margin is not None:
        evidence.append(
            {
                "source": "PLM classification margin",
                "claim": (
                    f"Top-1 vs Top-2 classification margin = "
                    f"{classification_margin:.4f}"
                ),
            }
        )

    # ---------------------------------------------------------
    # 3. Why might this matter?
    # ---------------------------------------------------------

    if predicted_category:
        why_it_might_matter = (
    f"The PLM findings provide a computational clue that the "
    f"sequence may be associated with a {predicted_category} "
    f"feature. This can help prioritize downstream analysis, "
    f"but the prediction and PLM evidence do not by itself "
    f"establish biological function."
        )
        )
    else:
        why_it_might_matter = (
            "The available computational findings may provide useful "
            "clues for prioritizing downstream investigation, but they "
            "do not by themselves establish biological function."
        )

    # ---------------------------------------------------------
    # 4. Next investigations
    # ---------------------------------------------------------

    next_investigations: List[str] = [
        "Validate the predicted category against trusted domain or annotation databases.",
        "Investigate whether the conserved region overlaps a known functional domain.",
        "Check whether variable positions overlap predicted or experimentally characterized functional regions.",
        "Compare the PLM prediction with independent sequence or structural evidence.",
    ]

    if latent_distance is not None:
        next_investigations.append(
            "Inspect the nearest latent reference sequences or clusters "
            "to determine which features drive the PLM similarity."
        )

    # ---------------------------------------------------------
    # 5. Limitations
    # ---------------------------------------------------------

    limitations: List[str] = [
        "PLM predictions are computational evidence and do not by themselves establish biological function.",
        "Latent similarity should not be interpreted as proof of functional equivalence.",
        "The reported confidence signals depend on the reference data and model used by the backend.",
        "Experimental or independent computational validation is required before assigning a confirmed biological function.",
    ]

    # ---------------------------------------------------------
    # 6. Confidence
    # ---------------------------------------------------------

    # This is an interpretation-level heuristic, not a calibrated
    # probability of biological correctness.
    if (
        latent_similarity is not None
        and classification_margin is not None
        and latent_similarity >= 0.80
        and classification_margin >= 0.30
    ):
        confidence = "high"
    elif (
        latent_similarity is not None
        and classification_margin is not None
        and latent_similarity >= 0.60
        and classification_margin >= 0.15
    ):
        confidence = "moderate"
    else:
        confidence = "low"

    return {
        "what_am_i_seeing": (
            " ".join(observations)
            or "No interpretable findings were supplied."
        ),
        "why_it_might_matter": why_it_might_matter,
        "next_investigations": next_investigations,
        "evidence": evidence,
        "limitations": limitations,
        "confidence": confidence,
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
