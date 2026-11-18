#!/usr/bin/env python3
"""Create the Set 2 analysis table with documented form-error exclusions."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "study/results/set2_combined_responses.csv"
OUTPUT = ROOT / "study/results/set2_participant_item_deidentified.csv"
EXCLUDED_MAIN_ORDERS = {"7", "11"}


def main() -> None:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        source_fields = list(rows[0])

    fields = source_fields + ["analysis_status", "exclusion_reason"]
    for row in rows:
        form_error = row["phase"] == "main" and row["study_order"] in EXCLUDED_MAIN_ORDERS
        row["analysis_status"] = "excluded" if form_error else "included"
        row["exclusion_reason"] = (
            "Form C explanation referred to a different legitimate screenshot; excluded from all conditions"
            if form_error
            else ""
        )
        if form_error and row["condition"] == "ai_explanation":
            row["ai_correctness"] = "form_error"

    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} Set 2 rows with documented exclusions to {OUTPUT}")


if __name__ == "__main__":
    main()
