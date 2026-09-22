import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from phishlens.validation import ValidationError, validate_llm_output


def valid_payload():
    return {
        "sample_id": "TEST-001",
        "verdict": "phishing",
        "confidence": 91,
        "claimed_brand": "Example Brand",
        "evidence": [
            {
                "category": "url_domain",
                "observation": "The supplied domain differs from the displayed brand.",
                "risk_relevance": "A brand-domain mismatch can indicate impersonation.",
            }
        ],
        "explanation": "The page may be impersonating the displayed brand.",
        "recommended_action": "leave_page",
        "needs_human_review": False,
    }


class ValidationTests(unittest.TestCase):
    def test_valid_payload(self):
        validate_llm_output(valid_payload())

    def test_confidence_out_of_range(self):
        payload = valid_payload()
        payload["confidence"] = 101
        with self.assertRaises(ValidationError):
            validate_llm_output(payload)

    def test_unknown_verdict(self):
        payload = valid_payload()
        payload["verdict"] = "safe"
        with self.assertRaises(ValidationError):
            validate_llm_output(payload)

    def test_extra_key(self):
        payload = valid_payload()
        payload["hidden_reasoning"] = "not allowed"
        with self.assertRaises(ValidationError):
            validate_llm_output(payload)


if __name__ == "__main__":
    unittest.main()
