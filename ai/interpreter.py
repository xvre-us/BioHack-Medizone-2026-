"""Evidence-grounded interpretation layer for Mystery Gene Decoder.

This module converts structured sequence-analysis findings into a small,
UI-friendly interpretation while keeping computational predictions clearly
separate from confirmed biological function.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


Result = Dict[str, Any]


def _as_float(value: Any) -> Optional[float]:
    """Return a finite float when possible; otherwise return None."""
    if isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if number != number:
        return None

    if abs(number) == float("inf"):
        return None

    return number


def _as_list(value: Any) -> List[Any]:
    """Normalize list-like input without crashing on malformed findings."""
    if isinstance(value, list):
        return value

    return []


def _format_probability(value: Any) -> Optional[str]:
    """Format a probability as a percentage when it is numeric."""
    number = _as_float(value)

    if number is None:
        return None

    # The backend contract stores probabilities in the 0-1 range.
    if 0 <= number <= 1:
        return f"{number:.1%}"

    return f"{number:.2f}"


def interpret_findings(findings: Dict[str, Any]) -> Result:
    """Interpret structured PLM/bioinformatics findings safely.

    The returned object is deliberately evidence-grounded:

    - model predictions are described as computational clues;
    - supplied annotations are preserved as evidence;
    - confidence is an interpretation-level heuristic, not a probability
      that the predicted biological function is correct.
    """

    if not isinstance(findings, dict):
        findings = {}

    # ---------------------------------------------------------
    # Input extraction
    # ---------------------------------------------------------

    sequence_length = findings.get("sequence_length")

    confidence_signals = findings.get("confidence_signals")

    if not isinstance(confidence_signals, dict):
        confidence_signals = {}

    latent_similarity = _as_float(
        confidence_signals.get("latent_similarity_score")
    )

    classification_margin = _as_float(
        confidence_signals.get("classification_margin")
    )

    plm_findings = findings.get("plm_findings")

    if not isinstance(plm_findings, dict):
        plm_findings = {}

    predicted_category = plm_findings.get(
        "predicted_functional_category"
    )

    if (
        not isinstance(predicted_category, str)
        or not predicted_category.strip()
    ):
        predicted_category = None

    top_predictions = _as_list(
        plm_findings.get("top_predictions")
    )

    nearest_clusters = _as_list(
        plm_findings.get("nearest_latent_clusters")
    )

    latent_distance = _as_float(
        plm_findings.get("latent_distance")
    )

    conserved_regions = _as_list(
        findings.get("conserved_regions")
    )

    variable_positions = _as_list(
        findings.get("variable_positions")
    )

    annotations = _as_list(
        findings.get("annotations")
    )

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
            "The PLM analysis places the sequence in the "
            f"'{predicted_category}' functional category."
        )

    # Top-ranked PLM prediction
    if top_predictions:
        top_prediction = top_predictions[0]

        if isinstance(top_prediction, dict):
            label = top_prediction.get("label")

            probability = _format_probability(
                top_prediction.get("probability")
            )

            if (
                isinstance(label, str)
                and label.strip()
                and probability is not None
            ):
                observations.append(
                    f"The top model prediction is '{label}' "
                    f"with a reported probability of {probability}."
                )

    # Nearest latent clusters
    valid_clusters = [
        str(cluster)
        for cluster in nearest_clusters
        if cluster is not None
        and str(cluster).strip()
    ]

    if valid_clusters:
        observations.append(
            "The sequence is closest in latent space to: "
            f"{', '.join(valid_clusters)}."
        )

    # Conserved regions
    if conserved_regions:
        observations.append(
            f"{len(conserved_regions)} conserved region(s) were reported."
        )

    # Variable positions
    if variable_positions:
        observations.append(
            f"{len(variable_positions)} variable position(s) were reported."
        )

    # ---------------------------------------------------------
    # 2. Evidence
    # ---------------------------------------------------------

    evidence: List[Dict[str, str]] = []

    for annotation in annotations:

        if not isinstance(annotation, dict):
            continue

        source = annotation.get(
            "source",
            "Unknown source"
        )

        if (
            not isinstance(source, str)
            or not source.strip()
        ):
            source = "Unknown source"

        description = (
            annotation.get("description")
            or annotation.get("label")
            or "Unspecified annotation"
        )

        if not isinstance(description, str):
            description = str(description)

        evidence.append(
            {
                "source": source,
                "claim": description,
            }
        )

    # PLM latent similarity
    if latent_similarity is not None:
        evidence.append(
            {
                "source": "PLM latent similarity",
                "claim": (
                    "Latent similarity score = "
                    f"{latent_similarity:.4f}"
                ),
            }
        )

    # PLM classification margin
    if classification_margin is not None:
        evidence.append(
            {
                "source": "PLM classification margin",
                "claim": (
                    "Top-1 vs Top-2 classification margin = "
                    f"{classification_margin:.4f}"
                ),
            }
        )

    # ---------------------------------------------------------
    # 3. Why might this matter?
    # ---------------------------------------------------------

    if predicted_category:

        why_it_might_matter = (
            "The PLM findings provide a computational clue that the "
            f"sequence may be associated with a {predicted_category} "
            "feature. This can help prioritize downstream analysis, "
            "but the prediction and PLM evidence do not by itself "
            "establish biological function."
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

        (
            "Validate the predicted category against trusted domain "
            "or annotation databases."
        ),

        (
            "Investigate whether the conserved region overlaps "
            "a known functional domain."
        ),

        (
            "Check whether variable positions overlap predicted "
            "or experimentally characterized sites."
        ),

        (
            "Compare the PLM prediction with independent sequence "
            "or structural evidence."
        ),
    ]

    if latent_distance is not None:

        next_investigations.append(
            "Inspect the nearest latent reference sequences or "
            "clusters to determine which features drive the "
            "PLM similarity."
        )

    # ---------------------------------------------------------
    # 5. Limitations
    # ---------------------------------------------------------

    limitations: List[str] = [

        (
            "PLM predictions are computational evidence and do not "
            "by themselves establish biological function."
        ),

        (
            "Latent similarity should not be interpreted as proof "
            "of functional equivalence."
        ),

        (
            "The reported confidence signals depend on the reference "
            "data and model used by the backend."
        ),

        (
            "Experimental or independent computational validation "
            "is required before assigning a confirmed biological "
            "function."
        ),
    ]

    # ---------------------------------------------------------
    # 6. Confidence
    # ---------------------------------------------------------

    # This is an interpretation-level heuristic, NOT a calibrated
    # probability of biological correctness.
    #
    # Both PLM signals must be present for moderate/high confidence.

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

    # ---------------------------------------------------------
    # 7. Final structured result
    # ---------------------------------------------------------

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


# -------------------------------------------------------------
# Standalone execution
# -------------------------------------------------------------

if __name__ == "__main__":

    input_path = Path(__file__).with_name(
        "mock_input.json"
    )

    findings = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    result = interpret_findings(findings)

    print(
        json.dumps(
            result,
            indent=2
        )
    )
