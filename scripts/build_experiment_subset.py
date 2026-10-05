#!/usr/bin/env python3
"""Build the balanced PhishLens pilot, main, and transfer manifests."""

from __future__ import annotations

import argparse
import csv
import random
import re
from collections import Counter, defaultdict
from pathlib import Path


PILOT_BRANDS = ["netflix", "spotify", "youtube"]
MAIN_BRANDS = [
    "facebook",
    "instagram",
    "linkedin",
    "whatsapp",
    "paypal",
    "wellsfargobank",
    "bankofamerica",
    "capitalone",
    "tdbank",
    "absabank",
    "outlook",
    "onedrive",
    "google",
    "apple",
    "adobe",
    "amazon",
    "ebay",
    "dropbox",
    "alibaba",
    "dhl",
    "chronopostinternational",
]
TRANSFER_BRANDS = ["steam", "att", "orange", "godaddy", "yahoo"]

ADVERSARIAL_TYPES = ["cw", "fgm", "pgd", "srnet", "swin", "vit"]
VISIBLE_TYPES = [
    "blur",
    "case_change",
    "color_change",
    "flipping",
    "font_change",
    "integration",
    "location_change",
    "omission",
    "replacement",
    "resizing",
    "rotation",
    "scaling",
]
PILOT_VARIANTS = {
    "netflix": "swin",
    "spotify": "vit",
    "youtube": "srnet",
}

COLUMNS = [
    "experiment_sample_id",
    "split",
    "study_role",
    "run_order",
    "context_pair_id",
    "source_sample_id",
    "brand",
    "ground_truth",
    "context_type",
    "displayed_url",
    "screenshot_path",
    "archive_path",
    "archive_member",
    "variant_family",
    "manipulation_type",
    "manipulation_parameter",
    "reviewer_1",
    "reviewer_2",
    "approval_status",
    "notes",
]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def brand_from_original(row: dict[str, str]) -> str:
    marker = "brand="
    if marker not in row["notes"]:
        raise ValueError(f"Missing brand metadata for {row['sample_id']}")
    return normalize(row["notes"].split(marker, 1)[1].split(";", 1)[0])


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def official_urls(
    originals_by_brand: dict[str, dict[str, dict[str, str]]]
) -> dict[str, str]:
    return {
        brand: labels["legitimate"]["displayed_url"]
        for brand, labels in originals_by_brand.items()
    }


def synthetic_url(brand: str) -> str:
    """Return a non-resolving URL under the reserved .test top-level domain."""
    return f"https://secure-{brand}.test/login"


def original_row(
    split: str,
    sequence: int,
    source: dict[str, str],
    brand: str,
) -> dict[str, str]:
    label = source["ground_truth"]
    return {
        "experiment_sample_id": f"{split}-original-{sequence:03d}-{label}",
        "split": split,
        "study_role": (
            "unaided_transfer" if split == "transfer" else "model_evaluation"
        ),
        "run_order": "",
        "context_pair_id": "",
        "source_sample_id": source["sample_id"],
        "brand": brand,
        "ground_truth": label,
        "context_type": "source_recorded",
        "displayed_url": source["displayed_url"],
        "screenshot_path": source["screenshot_path"],
        "archive_path": "",
        "archive_member": "",
        "variant_family": "original",
        "manipulation_type": "original",
        "manipulation_parameter": "",
        "reviewer_1": "",
        "reviewer_2": "",
        "approval_status": "pending",
        "notes": "Ground truth inherited from the reviewed source manifest",
    }


def variant_context_rows(
    split: str,
    sequence: int,
    variant: dict[str, str],
    official_url: str,
) -> list[dict[str, str]]:
    brand = normalize(variant["brand"])
    pair_id = f"{split}-context-{sequence:03d}"
    common = {
        "split": split,
        "study_role": "model_evaluation",
        "run_order": "",
        "context_pair_id": pair_id,
        "source_sample_id": variant["variant_id"],
        "brand": brand,
        "screenshot_path": variant["screenshot_path"],
        "archive_path": variant["archive_path"],
        "archive_member": variant["archive_member"],
        "variant_family": variant["variant_family"],
        "manipulation_type": variant["manipulation_type"],
        "manipulation_parameter": variant["manipulation_parameter"],
        "reviewer_1": "",
        "reviewer_2": "",
        "approval_status": "pending",
    }
    return [
        {
            "experiment_sample_id": f"{pair_id}-legitimate",
            **common,
            "ground_truth": "legitimate",
            "context_type": "official_domain_control",
            "displayed_url": official_url,
            "notes": "Controlled visual variant paired with its official domain",
        },
        {
            "experiment_sample_id": f"{pair_id}-phishing",
            **common,
            "ground_truth": "phishing",
            "context_type": "synthetic_domain_mismatch",
            "displayed_url": synthetic_url(brand),
            "notes": "Simulated phishing context uses the reserved .test domain",
        },
    ]


def choose_visible(
    variants: list[dict[str, str]], manipulation_type: str
) -> list[dict[str, str]]:
    candidates = [
        row
        for row in variants
        if row["manipulation_type"] == manipulation_type
        and normalize(row["brand"]) in {"absabank", "adobe", "alibaba"}
    ]
    by_brand: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        by_brand[normalize(row["brand"])].append(row)
    for values in by_brand.values():
        values.sort(key=lambda row: row["variant_id"])

    selected: list[dict[str, str]] = []
    for brand in ("absabank", "adobe", "alibaba"):
        values = by_brand.get(brand, [])
        if values:
            selected.append(values[len(values) // 2])

    if len(selected) < 3:
        used = {row["variant_id"] for row in selected}
        remaining = sorted(
            (row for row in candidates if row["variant_id"] not in used),
            key=lambda row: row["variant_id"],
        )
        selected.extend(remaining[: 3 - len(selected)])
    if len(selected) != 3:
        raise ValueError(f"Need three visible variants for {manipulation_type}")
    return selected


def choose_adversarial(
    variants: list[dict[str, str]], manipulation_type: str, offset: int
) -> list[dict[str, str]]:
    visible_brands = {"absabank", "adobe", "alibaba"}
    eligible_brands = [brand for brand in MAIN_BRANDS if brand not in visible_brands]
    rotated = eligible_brands[offset:] + eligible_brands[:offset]
    selected: list[dict[str, str]] = []
    for brand in rotated:
        match = next(
            (
                row
                for row in variants
                if row["manipulation_type"] == manipulation_type
                and normalize(row["brand"]) == brand
            ),
            None,
        )
        if match:
            selected.append(match)
        if len(selected) == 3:
            break
    if len(selected) != 3:
        raise ValueError(f"Need three adversarial variants for {manipulation_type}")
    return selected


def assign_run_order(rows: list[dict[str, str]]) -> None:
    rng = random.Random(469)
    for split in ("pilot", "main", "transfer"):
        split_rows = [row for row in rows if row["split"] == split]
        rng.shuffle(split_rows)
        for order, row in enumerate(split_rows, start=1):
            row["run_order"] = str(order)


def validate(rows: list[dict[str, str]]) -> None:
    ids = [row["experiment_sample_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Experiment sample IDs are not unique")
    split_brands: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        split_brands[row["split"]].add(row["brand"])
    for left, right in (("pilot", "main"), ("pilot", "transfer"), ("main", "transfer")):
        overlap = split_brands[left] & split_brands[right]
        if overlap:
            raise ValueError(f"Brand leakage between {left} and {right}: {overlap}")

    main = [row for row in rows if row["split"] == "main"]
    labels = Counter(row["ground_truth"] for row in main)
    if labels != {"legitimate": 75, "phishing": 75}:
        raise ValueError(f"Main split is not balanced: {labels}")
    main_variant_types = Counter(
        row["manipulation_type"]
        for row in main
        if row["variant_family"] != "original"
        and row["context_type"] == "official_domain_control"
    )
    if set(main_variant_types) != set(ADVERSARIAL_TYPES + VISIBLE_TYPES):
        raise ValueError("Main split does not cover all manipulation types")
    if any(count != 3 for count in main_variant_types.values()):
        raise ValueError(f"Expected three screenshots per manipulation: {main_variant_types}")
    if any(row["approval_status"] != "pending" for row in rows):
        raise ValueError("New selections must remain pending independent review")


def build_subset(
    originals: list[dict[str, str]], variants: list[dict[str, str]]
) -> list[dict[str, str]]:
    originals_by_brand: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in originals:
        originals_by_brand[brand_from_original(row)][row["ground_truth"]] = row
    urls = official_urls(originals_by_brand)
    rows: list[dict[str, str]] = []

    for split, brands in (("pilot", PILOT_BRANDS), ("main", MAIN_BRANDS)):
        sequence = 1
        for brand in brands:
            for label in ("legitimate", "phishing"):
                rows.append(
                    original_row(
                        split, sequence, originals_by_brand[brand][label], brand
                    )
                )
                sequence += 1

    pilot_selected = []
    for brand, method in PILOT_VARIANTS.items():
        pilot_selected.append(
            next(
                row
                for row in variants
                if normalize(row["brand"]) == brand
                and row["manipulation_type"] == method
            )
        )
    for index, variant in enumerate(pilot_selected, start=1):
        brand = normalize(variant["brand"])
        rows.extend(variant_context_rows("pilot", index, variant, urls[brand]))

    main_selected: list[dict[str, str]] = []
    for offset, method in enumerate(ADVERSARIAL_TYPES):
        main_selected.extend(choose_adversarial(variants, method, offset * 3))
    for method in VISIBLE_TYPES:
        main_selected.extend(choose_visible(variants, method))
    for index, variant in enumerate(main_selected, start=1):
        brand = normalize(variant["brand"])
        rows.extend(variant_context_rows("main", index, variant, urls[brand]))

    transfer_labels = ["legitimate", "phishing", "legitimate", "phishing", "phishing"]
    for sequence, (brand, label) in enumerate(
        zip(TRANSFER_BRANDS, transfer_labels), start=1
    ):
        rows.append(
            original_row(
                "transfer", sequence, originals_by_brand[brand][label], brand
            )
        )

    assign_run_order(rows)
    rows.sort(key=lambda row: (row["split"], int(row["run_order"])))
    validate(rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-manifest", type=Path, default=Path("data/manifest.csv"))
    parser.add_argument(
        "--variant-manifest", type=Path, default=Path("data/controlled_variants.csv")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/experiment_subset.csv")
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    original_path = args.original_manifest if args.original_manifest.is_absolute() else repo_root / args.original_manifest
    variant_path = args.variant_manifest if args.variant_manifest.is_absolute() else repo_root / args.variant_manifest
    output = args.output if args.output.is_absolute() else repo_root / args.output

    rows = build_subset(read_csv(original_path), read_csv(variant_path))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} experiment records to {output}")
    print("Splits:", dict(sorted(Counter(row["split"] for row in rows).items())))
    print("Main labels:", dict(Counter(row["ground_truth"] for row in rows if row["split"] == "main")))


if __name__ == "__main__":
    main()
