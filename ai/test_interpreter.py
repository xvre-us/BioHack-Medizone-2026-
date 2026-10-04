import json
from pathlib import Path

from interpreter import interpret_findings


def load_mock_input():
    """Load the current mock PLM findings used by the AI interpretation layer."""
    input_path = Path(__file__).with_name("mock_input.json")

    return json.loads(
        input_path.read_text(encoding="utf-8")
    )


def test_interpreter_output_structure():
    """Verify that the interpreter returns the complete expected output contract."""
    findings = load_mock_input()

    result = interpret_findings(findings)

    required_fields = {
        "what_am_i_seeing",
        "why_it_might_matter",
        "next_investigations",
        "evidence",
        "limitations",
        "confidence",
    }

    assert required_fields.issubset(result.keys())

    assert isinstance(result["what_am_i_seeing"], str)
    assert isinstance(result["why_it_might_matter"], str)
    assert isinstance(result["next_investigations"], list)
    assert isinstance(result["evidence"], list)
    assert isinstance(result["limitations"], list)

    assert result["confidence"] in {
        "low",
        "moderate",
        "high",
    }


def test_mock_input_with_plm_findings():
    """
    Verify that the current mock input containing PLM findings
    and confidence signals is interpreted successfully.
    """
    findings = load_mock_input()

    result = interpret_findings(findings)

    assert result["confidence"] == "high"

    assert "1247 residues" in result["what_am_i_seeing"]
    assert "kinase_like_domain" in result["what_am_i_seeing"]
    assert "Serine/threonine protein kinase" in result["what_am_i_seeing"]

    assert "kinase_catalytic_domain" in result["what_am_i_seeing"]
    assert "atp_binding_site" in result["what_am_i_seeing"]

    assert "1 conserved region(s)" in result["what_am_i_seeing"]
    assert "3 variable position(s)" in result["what_am_i_seeing"]


def test_confidence_signals_are_reported_as_evidence():
    """Verify that both backend confidence signals are surfaced as evidence."""
    findings = load_mock_input()

    result = interpret_findings(findings)

    evidence_sources = {
        item["source"]
        for item in result["evidence"]
    }

    assert "PLM latent similarity" in evidence_sources
    assert "PLM classification margin" in evidence_sources

    evidence_claims = [
        item["claim"]
        for item in result["evidence"]
    ]

    assert any(
        "0.8421" in claim
        for claim in evidence_claims
    )

    assert any(
        "0.3815" in claim
        for claim in evidence_claims
    )


def test_confidence_is_high_for_strong_plm_signals():
    """
    High confidence requires both:
    - latent similarity >= 0.80
    - classification margin >= 0.30
    """
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.80,
            "classification_margin": 0.30,
        },
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert result["confidence"] == "high"


def test_confidence_is_moderate_for_intermediate_plm_signals():
    """
    Moderate confidence requires both:
    - latent similarity >= 0.60
    - classification margin >= 0.15
    while not meeting the high-confidence thresholds.
    """
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.70,
            "classification_margin": 0.20,
        },
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert result["confidence"] == "moderate"


def test_confidence_is_low_for_weak_plm_signals():
    """Weak confidence signals should produce low interpretation confidence."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.40,
            "classification_margin": 0.10,
        },
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert result["confidence"] == "low"


def test_confidence_is_low_when_signals_are_missing():
    """
    Missing confidence signals must not result in a high or moderate
    confidence interpretation.
    """
    findings = {
        "sequence_length": 1000,
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert result["confidence"] == "low"
    assert result["evidence"] == []


def test_confidence_is_low_when_only_one_signal_is_available():
    """Both PLM confidence signals are required for moderate/high confidence."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.90,
        },
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert result["confidence"] == "low"


def test_interpreter_reports_conserved_regions():
    """Verify that conserved regions are included in the observations."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.70,
            "classification_margin": 0.20,
        },
        "plm_findings": {},
        "conserved_regions": [
            {
                "start": 100,
                "end": 200,
                "evidence": "Conserved region detected",
            }
        ],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert "conserved region" in result["what_am_i_seeing"]
    assert result["confidence"] == "moderate"


def test_interpreter_reports_variable_positions():
    """Verify that variable positions are reported."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.70,
            "classification_margin": 0.20,
        },
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [100, 250, 500],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert "3 variable position(s)" in result["what_am_i_seeing"]


def test_interpreter_reports_annotations_as_evidence():
    """Verify that supplied annotations become evidence entries."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {},
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [
            {
                "source": "BLASTp (nr)",
                "label": "hypothetical protein",
                "description": "No significant similarity found",
                "evidence": "E-value > 0.05",
            }
        ],
    }

    result = interpret_findings(findings)

    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["source"] == "BLASTp (nr)"
    assert result["evidence"][0]["claim"] == (
        "No significant similarity found"
    )


def test_interpreter_uses_annotation_label_when_description_is_missing():
    """Verify the annotation label is used as an evidence fallback."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {},
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [
            {
                "source": "Mock database",
                "label": "unknown protein",
                "description": None,
            }
        ],
    }

    result = interpret_findings(findings)

    assert result["evidence"][0]["source"] == "Mock database"
    assert result["evidence"][0]["claim"] == "unknown protein"


def test_interpreter_reports_top_prediction():
    """Verify that the highest-ranked PLM prediction is surfaced."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.80,
            "classification_margin": 0.30,
        },
        "plm_findings": {
            "predicted_functional_category": "kinase_like_domain",
            "top_predictions": [
                {
                    "label": "Serine/threonine protein kinase",
                    "probability": 0.6412,
                },
                {
                    "label": "ATP-binding cassette transporter",
                    "probability": 0.2597,
                },
            ],
            "nearest_latent_clusters": [],
            "latent_distance": 0.1579,
        },
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert "Serine/threonine protein kinase" in (
        result["what_am_i_seeing"]
    )

    assert "64.1%" in result["what_am_i_seeing"]


def test_interpreter_reports_nearest_latent_clusters():
    """Verify that nearest PLM latent clusters are surfaced."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {},
        "plm_findings": {
            "predicted_functional_category": "kinase_like_domain",
            "top_predictions": [],
            "nearest_latent_clusters": [
                "kinase_catalytic_domain",
                "atp_binding_site",
            ],
            "latent_distance": 0.1579,
        },
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert "kinase_catalytic_domain" in result["what_am_i_seeing"]
    assert "atp_binding_site" in result["what_am_i_seeing"]


def test_interpreter_adds_latent_distance_investigation():
    """Verify that latent distance triggers a relevant next investigation."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {},
        "plm_findings": {
            "predicted_functional_category": "kinase_like_domain",
            "top_predictions": [],
            "nearest_latent_clusters": [],
            "latent_distance": 0.1579,
        },
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert any(
        "nearest latent reference sequences" in investigation
        for investigation in result["next_investigations"]
    )


def test_interpreter_does_not_claim_confirmed_gene_function():
    """
    PLM predictions must remain computational clues rather than
    confirmed biological function.
    """
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.95,
            "classification_margin": 0.50,
        },
        "plm_findings": {
            "predicted_functional_category": "kinase_like_domain",
            "top_predictions": [
                {
                    "label": "Serine/threonine protein kinase",
                    "probability": 0.90,
                }
            ],
            "nearest_latent_clusters": [],
            "latent_distance": 0.10,
        },
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert (
        "do not by itself establish biological function"
        in result["why_it_might_matter"]
    )

    assert any(
        "do not by themselves establish biological function"
        in limitation
        for limitation in result["limitations"]
    )


def test_interpreter_limitation_mentions_latent_similarity():
    """Verify that latent similarity is explicitly treated as non-proof."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.95,
            "classification_margin": 0.50,
        },
        "plm_findings": {},
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert any(
        "Latent similarity should not be interpreted as proof"
        in limitation
        for limitation in result["limitations"]
    )


def test_interpreter_handles_empty_findings():
    """Verify graceful behavior when no findings are supplied."""
    findings = {}

    result = interpret_findings(findings)

    assert isinstance(result["what_am_i_seeing"], str)
    assert isinstance(result["why_it_might_matter"], str)
    assert isinstance(result["next_investigations"], list)
    assert isinstance(result["evidence"], list)
    assert isinstance(result["limitations"], list)
    assert result["confidence"] == "low"


def test_interpreter_handles_missing_plm_fields():
    """Verify that incomplete PLM findings do not crash the interpreter."""
    findings = {
        "sequence_length": 1247,
        "confidence_signals": {
            "latent_similarity_score": 0.84,
            "classification_margin": 0.38,
        },
        "plm_findings": {
            "predicted_functional_category": "kinase_like_domain",
        },
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert result["confidence"] == "high"
    assert "kinase_like_domain" in result["what_am_i_seeing"]


def test_interpreter_handles_no_annotations():
    """Verify that interpretation still works without annotations."""
    findings = {
        "sequence_length": 1000,
        "confidence_signals": {
            "latent_similarity_score": 0.80,
            "classification_margin": 0.30,
        },
        "plm_findings": {
            "predicted_functional_category": "kinase_like_domain",
            "top_predictions": [],
            "nearest_latent_clusters": [],
            "latent_distance": 0.2,
        },
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": [],
    }

    result = interpret_findings(findings)

    assert result["confidence"] == "high"
    assert len(result["evidence"]) == 2

    evidence_sources = {
        item["source"]
        for item in result["evidence"]
    }

    assert "PLM latent similarity" in evidence_sources
    assert "PLM classification margin" in evidence_sources
