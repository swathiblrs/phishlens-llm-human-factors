#!/usr/bin/env python3
"""Validate one normalized PhishLens JSON result."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from phishlens.validation import ValidationError, validate_llm_output  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_result.py RESULT.json", file=sys.stderr)
        return 2

    result_path = Path(sys.argv[1])
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        validate_llm_output(payload)
    except FileNotFoundError:
        print(f"File not found: {result_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Valid PhishLens result: {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
