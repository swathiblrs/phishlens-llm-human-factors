#!/usr/bin/env python3
"""Build the publication-scale main-extra screenshot review package.

The script preserves the existing pilot, main, and transfer packages. It selects
only controlled variants from the established main-study brands, plus the
unused webmail brand, and excludes any image already present in the original
110-screenshot review set.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image


REVIEWER = "Swathi Bangalore Satish"
TRANSFER_BRANDS = {"att", "godaddy", "orange", "steam", "yahoo"}
PILOT_BRANDS = {"netflix", "spotify", "youtube"}

COLUMNS = [
    "review_item_id",
    "split",
    "relative_image_path",
    "experiment_sample_ids",
    "context_pair_id",
    "source_variant_id",
    "brand",
    "variant_family",
    "manipulation_type",
    "manipulation_parameter",
    "image_width",
    "image_height",
    "content_sha256",
    "contexts_to_verify",
    "assigned_reviewer_1",
    "assigned_reviewer_2",
    "reviewer_1_decision",
    "reviewer_1_notes",
    "reviewer_2_decision",
    "reviewer_2_notes",
    "disagreement",
    "final_status",
]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def source_bytes(repo_root: Path, row: dict[str, str]) -> bytes:
    if row["screenshot_path"]:
        source = (repo_root / row["screenshot_path"]).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        return source.read_bytes()

    archive = (repo_root / row["archive_path"]).resolve()
    if not archive.is_file():
        raise FileNotFoundError(archive)
    with zipfile.ZipFile(archive) as handle:
        try:
            return handle.read(row["archive_member"])
        except KeyError as error:
            raise FileNotFoundError(row["archive_member"]) from error


def verify_image(data: bytes) -> tuple[int, int]:
    if not data:
        raise ValueError("Empty image file")
    with Image.open(io.BytesIO(data)) as image:
        width, height = image.size
        image.verify()
    if width < 1 or height < 1:
        raise ValueError(f"Invalid image dimensions: {width}x{height}")
    return width, height


def existing_hashes(review_root: Path) -> set[str]:
    hashes: set[str] = set()
    for split in ("pilot", "main", "transfer"):
        for image in (review_root / split / "screenshots").glob("*"):
            if image.is_file():
                hashes.add(hashlib.sha256(image.read_bytes()).hexdigest())
    return hashes


def official_urls(manifest_rows: list[dict[str, str]]) -> dict[str, str]:
    urls: dict[str, str] = {}
    for row in manifest_rows:
        if row["ground_truth"] != "legitimate" or "brand=" not in row["notes"]:
            continue
        brand = normalize(row["notes"].split("brand=", 1)[1].split(";", 1)[0])
        urls[brand] = row["displayed_url"]
    return urls


def main_brands(review_root: Path) -> set[str]:
    brands = {
        normalize(row["brand"])
        for row in read_csv(review_root / "main" / "main_review.csv")
    }
    # Webmail is present in the source manifest but was not used by pilot,
    # main, or transfer. It expands brand coverage without contaminating the
    # held-out transfer brands.
    brands.add("webmail")
    return brands


def build(repo_root: Path, output_root: Path) -> tuple[list[dict[str, str]], Counter]:
    review_root = repo_root / "review"
    variants = read_csv(repo_root / "data" / "controlled_variants.csv")
    manifest = read_csv(repo_root / "data" / "manifest.csv")
    urls = official_urls(manifest)
    eligible_brands = main_brands(review_root)
    if eligible_brands & (TRANSFER_BRANDS | PILOT_BRANDS):
        raise ValueError("Main-extra brands overlap pilot or transfer brands")

    old_hashes = existing_hashes(review_root)
    seen_hashes: set[str] = set()
    kept: list[tuple[dict[str, str], bytes, str, int, int]] = []
    audit = Counter()

    for row in variants:
        brand = normalize(row["brand"])
        if brand not in eligible_brands:
            audit["excluded_non_main_brand"] += 1
            continue
        if brand not in urls:
            audit["excluded_missing_official_url"] += 1
            continue
        try:
            data = source_bytes(repo_root, row)
            width, height = verify_image(data)
        except (FileNotFoundError, KeyError, OSError, ValueError, zipfile.BadZipFile):
            audit["excluded_missing_or_broken"] += 1
            continue

        digest = hashlib.sha256(data).hexdigest()
        if digest in old_hashes:
            audit["excluded_already_in_110"] += 1
            continue
        if digest in seen_hashes:
            audit["excluded_duplicate_content"] += 1
            continue

        seen_hashes.add(digest)
        kept.append((row, data, digest, width, height))

    kept.sort(
        key=lambda item: (
            normalize(item[0]["brand"]),
            item[0]["variant_family"],
            item[0]["manipulation_type"],
            item[0]["variant_id"],
        )
    )

    screenshot_root = output_root / "screenshots"
    screenshot_root.mkdir(parents=True, exist_ok=True)
    review_rows: list[dict[str, str]] = []
    for index, (source, data, digest, width, height) in enumerate(kept, start=1):
        item_id = f"main-extra-{index:03d}"
        brand = normalize(source["brand"])
        context_id = f"main-extra-context-{index:03d}"
        filename = (
            f"{item_id}-{slug(brand)}-{slug(source['manipulation_type'])}.png"
        )
        relative_path = Path("screenshots") / filename
        (output_root / relative_path).write_bytes(data)
        official_url = urls[brand]
        synthetic_url = f"https://secure-{brand}.test/login"
        review_rows.append(
            {
                "review_item_id": item_id,
                "split": "main_extra",
                "relative_image_path": relative_path.as_posix(),
                "experiment_sample_ids": (
                    f"{context_id}-legitimate | {context_id}-phishing"
                ),
                "context_pair_id": context_id,
                "source_variant_id": source["variant_id"],
                "brand": brand,
                "variant_family": source["variant_family"],
                "manipulation_type": source["manipulation_type"],
                "manipulation_parameter": source["manipulation_parameter"],
                "image_width": str(width),
                "image_height": str(height),
                "content_sha256": digest,
                "contexts_to_verify": (
                    f"official_domain_control: {official_url} [legitimate] | "
                    f"synthetic_domain_mismatch: {synthetic_url} [phishing]"
                ),
                "assigned_reviewer_1": REVIEWER,
                "assigned_reviewer_2": "",
                "reviewer_1_decision": "",
                "reviewer_1_notes": "",
                "reviewer_2_decision": "",
                "reviewer_2_notes": "",
                "disagreement": "",
                "final_status": "pending",
            }
        )

    output_csv = output_root / "main_extra_review.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)

    audit["included"] = len(review_rows)
    audit["included_visible_manipulation"] = sum(
        row["variant_family"] == "visible_manipulation" for row in review_rows
    )
    audit["included_adversarial_perturbation"] = sum(
        row["variant_family"] == "adversarial_perturbation" for row in review_rows
    )
    audit["included_brands"] = len({row["brand"] for row in review_rows})
    return review_rows, audit


def validate(output_root: Path, rows: list[dict[str, str]]) -> None:
    if len(rows) != 259:
        raise ValueError(f"Expected 259 main-extra images, found {len(rows)}")
    ids = [row["review_item_id"] for row in rows]
    hashes = [row["content_sha256"] for row in rows]
    if len(ids) != len(set(ids)) or len(hashes) != len(set(hashes)):
        raise ValueError("Duplicate IDs or image hashes in main-extra package")
    for row in rows:
        image = output_root / row["relative_image_path"]
        if not image.is_file():
            raise FileNotFoundError(image)
        if hashlib.sha256(image.read_bytes()).hexdigest() != row["content_sha256"]:
            raise ValueError(f"Hash mismatch: {image}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root", type=Path, default=Path("review/main_extra")
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output_root = (
        args.output_root
        if args.output_root.is_absolute()
        else repo_root / args.output_root
    )
    if output_root.exists():
        raise FileExistsError(
            f"Output already exists: {output_root}. Remove it explicitly to rebuild."
        )

    rows, audit = build(repo_root, output_root)
    validate(output_root, rows)
    print("Created main-extra review package")
    for key in sorted(audit):
        print(f"  {key}: {audit[key]}")


if __name__ == "__main__":
    main()
