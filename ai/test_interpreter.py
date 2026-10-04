import json
from pathlib import Path

from interpreter import interpret_findings


def test_interpreter_output():
    input_path = Path(__file__).with_name("mock_input.json")

    findings = json.loads(
        input_path.read_text(encoding="utf-8")
    )

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
def test_interpreter_with_no_similarity():
    findings = {
        "sequence_length": 1000,
        "similarity": None,
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": []
    }

    result = interpret_findings(findings)

    assert result["confidence"] == "low"
    assert result["evidence"] == []


def test_interpreter_reports_conserved_regions():
    findings = {
        "sequence_length": 1000,
        "similarity": 0.80,
        "conserved_regions": [
            {"start": 100, "end": 200}
        ],
        "variable_positions": [],
        "annotations": [
            {
                "source": "mock",
                "description": "Conserved region detected"
            }
        ]
    }

    result = interpret_findings(findings)

    assert "conserved region" in result["what_am_i_seeing"]
    assert result["confidence"] == "moderate"


def test_interpreter_does_not_claim_gene_function():
    findings = {
        "sequence_length": 1000,
        "similarity": 0.95,
        "conserved_regions": [],
        "variable_positions": [],
        "annotations": []
    }

    result = interpret_findings(findings)

    assert "do not establish gene function" in result["limitations"][0]
