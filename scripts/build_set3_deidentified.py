#!/usr/bin/env python3
"""Build the de-identified Set 3 participant-by-item research table."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FIELDS = [
    "participant_id",
    "set",
    "condition",
    "study_order",
    "phase",
    "screenshot_id",
    "ground_truth",
    "ai_model",
    "ai_verdict",
    "ai_correctness",
    "participant_decision",
    "accuracy",
    "confidence",
    "trust",
]


def read_csv(path: Path) -> list[list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def load_mapping(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 17:
        raise ValueError("Set 3 mapping must contain 12 main and five transfer items")
    return rows


def parse_answer(value: str) -> tuple[str, str]:
    normalized = value.replace(",", "—", 1)
    parts = [part.strip().lower() for part in normalized.split("—")]
    if len(parts) != 2 or parts[0] not in {"legitimate", "phishing"}:
        raise ValueError(f"Unexpected classification response: {value!r}")
    confidence = parts[1].replace(" confidence", "")
    if confidence not in {"low", "medium", "high"}:
        raise ValueError(f"Unexpected confidence response: {value!r}")
    return parts[0], confidence


def build_condition(
    condition: str,
    source: Path,
    mapping: list[dict[str, str]],
) -> list[dict[str, str | int]]:
    rows = read_csv(source)
    if condition == "no_warning":
        decision_columns = list(range(7, 24))
        trust_columns: list[int | None] = [None] * 17
    else:
        decision_columns = list(range(7, 31, 2)) + list(range(31, 36))
        trust_columns = list(range(8, 32, 2)) + [None] * 5

    eligible = [row for row in rows[1:] if row[1].strip().lower().startswith("yes")]
    condition_code = {
        "no_warning": "A",
        "standard_warning": "B",
        "ai_explanation": "C",
    }[condition]
    output: list[dict[str, str | int]] = []

    for participant_number, source_row in enumerate(eligible, start=1):
        participant_id = f"S3-{condition_code}-{participant_number:03d}"
        for item, decision_column, trust_column in zip(mapping, decision_columns, trust_columns):
            decision, confidence = parse_answer(source_row[decision_column])
            is_ai_main = condition == "ai_explanation" and item["phase"] == "main"
            output.append(
                {
                    "participant_id": participant_id,
                    "set": "Set 3",
                    "condition": condition,
                    "study_order": item["study_order"],
                    "phase": item["phase"],
                    "screenshot_id": item["screenshot_id"],
                    "ground_truth": item["ground_truth"],
                    "ai_model": item["ai_model"] if is_ai_main else "",
                    "ai_verdict": item["ai_verdict"] if is_ai_main else "",
                    "ai_correctness": item["ai_correctness"] if is_ai_main else "",
                    "participant_decision": decision,
                    "accuracy": int(decision == item["ground_truth"]),
                    "confidence": confidence,
                    "trust": source_row[trust_column] if trust_column is not None else "",
                }
            )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--form-a", type=Path, required=True)
    parser.add_argument("--form-b", type=Path, required=True)
    parser.add_argument("--form-c", type=Path, required=True)
    parser.add_argument(
        "--mapping",
        type=Path,
        default=ROOT / "study/results/set3_form_mapping.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "study/results/set3_participant_item_deidentified.csv",
    )
    args = parser.parse_args()

    mapping = load_mapping(args.mapping)
    sources = {
        "no_warning": args.form_a,
        "standard_warning": args.form_b,
        "ai_explanation": args.form_c,
    }
    output = [
        row
        for condition, source in sources.items()
        for row in build_condition(condition, source, mapping)
    ]
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output)
    print(f"Wrote {len(output)} de-identified participant-item rows to {args.output}")


if __name__ == "__main__":
    main()
