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
