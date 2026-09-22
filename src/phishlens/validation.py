"""Strict validation for normalized PhishLens model outputs.

The validator intentionally uses only the Python standard library so the
repository can be checked before optional API dependencies are selected.
"""

from __future__ import annotations

from typing import Any


class ValidationError(ValueError):
    """Raised when a normalized model response violates the contract."""


REQUIRED_KEYS = {
    "sample_id",
    "verdict",
    "confidence",
    "claimed_brand",
    "evidence",
    "explanation",
    "recommended_action",
    "needs_human_review",
}

VERDICTS = {"phishing", "legitimate", "uncertain"}
ACTIONS = {"proceed", "verify_independently", "leave_page"}
EVIDENCE_CATEGORIES = {
    "url_domain",
    "branding",
    "credential_request",
    "layout",
    "security_indicator",
    "content",
    "other",
}


def _require_nonempty_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")


def validate_llm_output(payload: Any) -> None:
    """Validate a parsed JSON response.

    Raises:
        ValidationError: if the payload does not match the normalized contract.
    """

    if not isinstance(payload, dict):
        raise ValidationError("top-level value must be a JSON object")

    missing = REQUIRED_KEYS - payload.keys()
    extra = payload.keys() - REQUIRED_KEYS
    if missing:
        raise ValidationError(f"missing required keys: {sorted(missing)}")
    if extra:
        raise ValidationError(f"unexpected keys: {sorted(extra)}")

    _require_nonempty_string(payload["sample_id"], "sample_id")

    if payload["verdict"] not in VERDICTS:
        raise ValidationError(f"verdict must be one of {sorted(VERDICTS)}")

    confidence = payload["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, int):
        raise ValidationError("confidence must be an integer")
    if not 0 <= confidence <= 100:
        raise ValidationError("confidence must be between 0 and 100")

    brand = payload["claimed_brand"]
    if brand is not None:
        _require_nonempty_string(brand, "claimed_brand")

    evidence = payload["evidence"]
    if not isinstance(evidence, list):
        raise ValidationError("evidence must be an array")
    if len(evidence) > 8:
        raise ValidationError("evidence cannot contain more than 8 items")

    evidence_keys = {"category", "observation", "risk_relevance"}
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            raise ValidationError(f"evidence[{index}] must be an object")
        if set(item) != evidence_keys:
            raise ValidationError(
                f"evidence[{index}] must contain exactly {sorted(evidence_keys)}"
            )
        if item["category"] not in EVIDENCE_CATEGORIES:
            raise ValidationError(
                f"evidence[{index}].category must be one of "
                f"{sorted(EVIDENCE_CATEGORIES)}"
            )
        _require_nonempty_string(item["observation"], f"evidence[{index}].observation")
        _require_nonempty_string(
            item["risk_relevance"], f"evidence[{index}].risk_relevance"
        )

    _require_nonempty_string(payload["explanation"], "explanation")

    if payload["recommended_action"] not in ACTIONS:
        raise ValidationError(
            f"recommended_action must be one of {sorted(ACTIONS)}"
        )

    if not isinstance(payload["needs_human_review"], bool):
        raise ValidationError("needs_human_review must be a boolean")
