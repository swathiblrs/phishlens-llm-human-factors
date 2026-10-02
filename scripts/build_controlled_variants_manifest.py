#!/usr/bin/env python3
"""Catalog controlled visual variants without opening webpages or copying images."""

from __future__ import annotations

import argparse
import csv
import os
import re
import zipfile
from collections import Counter
from pathlib import Path


SOURCE_REFERENCE = (
    "Ji et al., USENIX Security 2025; "
    "https://moa-lab.net/evaluation-visual-similarity-based-phishing-detection-models/"
)

VISIBLE_MANIPULATIONS = {
    "01": "color_change",
    "02": "scaling",
    "03": "rotation",
    "04": "integration",
    "05": "location_change",
    "06": "flipping",
    "07": "replacement",
    "08": "blur",
    "09": "resizing",
    "10": "omission",
    "11": "case_change",
    "12": "font_change",
}

COLUMNS = [
    "variant_id",
    "brand",
    "variant_family",
    "manipulation_type",
    "manipulation_parameter",
    "screenshot_path",
    "archive_path",
    "archive_member",
    "parent_screenshot_path",
    "base_content_label",
    "experiment_label",
    "url_context_status",
    "review_status",
    "source_reference",
    "notes",
]


def repo_relative(path: Path, repo_root: Path) -> str:
    return os.path.relpath(path.resolve(), repo_root.resolve())


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parameter_slug(value: str) -> str:
    """Create an ID-safe value while preserving numeric sign and decimal point."""
    normalized = value.lower().replace("-", "neg-").replace(".", "p")
    return slug(normalized)


def parent_path(benign_root: Path, brand: str, repo_root: Path) -> str:
    candidate = benign_root / brand / "login.png"
    return repo_relative(candidate, repo_root) if candidate.is_file() else ""


def adversarial_rows(
    repo_root: Path, perturbation_root: Path, benign_root: Path
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    sources: list[tuple[str, Path, str]] = []

    for method in ("swin", "vit"):
        for path in sorted((perturbation_root / method).glob("*/screenshot_*.png")):
            sources.append((method, path, path.parent.name))

    for method in ("cw", "fgm", "pgd"):
        directory = perturbation_root / "white_box_attack" / f"{method}_screenshot"
        for path in sorted(directory.glob("*.png")):
            sources.append((method, path, path.stem))

    for path in sorted((perturbation_root / "srnet" / "text_screenshot").glob("*.png")):
        if path.name.endswith("_crop_logo.png"):
            continue
        sources.append(("srnet", path, path.stem.removesuffix("_srnet")))

    for method, path, brand in sources:
        rows.append(
            {
                "variant_id": f"adv-{method}-{slug(brand)}",
                "brand": brand,
                "variant_family": "adversarial_perturbation",
                "manipulation_type": method,
                "manipulation_parameter": method,
                "screenshot_path": repo_relative(path, repo_root),
                "archive_path": "",
                "archive_member": "",
                "parent_screenshot_path": parent_path(benign_root, brand, repo_root),
                "base_content_label": "legitimate",
                "experiment_label": "pending_url_context",
                "url_context_status": "not_assigned",
                "review_status": "pending",
                "source_reference": SOURCE_REFERENCE,
                "notes": "Full-page screenshot; logo-crop derivative excluded",
            }
        )
    return rows


def visible_rows(
    repo_root: Path, archives: list[Path], benign_root: Path
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    member_pattern = re.compile(
        r"^brand_(?P<brand>[^/]+)/(?P<code>\d{2})/(?P<name>[^/]+\.png)$"
    )

    for archive in sorted(archives):
        with zipfile.ZipFile(archive) as handle:
            for member in sorted(handle.namelist()):
                match = member_pattern.match(member)
                if not match or member.endswith("_crop_logo.png"):
                    continue
                code = match.group("code")
                if code not in VISIBLE_MANIPULATIONS:
                    continue

                brand = match.group("brand")
                name = match.group("name")
                prefix = f"{brand}_manipulation_{int(code)}_"
                parameter = Path(name).stem
                if parameter.startswith(prefix):
                    parameter = parameter[len(prefix) :]

                rows.append(
                    {
                        "variant_id": (
                            f"visible-{slug(brand)}-{code}-{parameter_slug(parameter)}"
                        ),
                        "brand": brand,
                        "variant_family": "visible_manipulation",
                        "manipulation_type": VISIBLE_MANIPULATIONS[code],
                        "manipulation_parameter": parameter,
                        "screenshot_path": "",
                        "archive_path": repo_relative(archive, repo_root),
                        "archive_member": member,
                        "parent_screenshot_path": parent_path(
                            benign_root, brand, repo_root
                        ),
                        "base_content_label": "legitimate",
                        "experiment_label": "pending_url_context",
                        "url_context_status": "not_assigned",
                        "review_status": "pending",
                        "source_reference": SOURCE_REFERENCE,
                        "notes": "Full-page screenshot stored in ZIP; crop excluded",
                    }
                )
    return rows


def validate(rows: list[dict[str, str]]) -> None:
    ids = [row["variant_id"] for row in rows]
    if len(ids) != len(set(ids)):
        duplicates = [key for key, count in Counter(ids).items() if count > 1]
        raise ValueError(f"Duplicate variant IDs: {duplicates[:5]}")
    if any(set(row) != set(COLUMNS) for row in rows):
        raise ValueError("A row does not match the controlled-variant schema")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--perturbation-root", type=Path, required=True)
    parser.add_argument("--benign-root", type=Path, required=True)
    parser.add_argument("--visible-archive", action="append", type=Path, default=[])
    parser.add_argument(
        "--output", type=Path, default=Path("data/controlled_variants.csv")
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else repo_root / args.output
    rows = adversarial_rows(repo_root, args.perturbation_root, args.benign_root)
    rows.extend(visible_rows(repo_root, args.visible_archive, args.benign_root))
    rows.sort(key=lambda row: (row["variant_family"], row["manipulation_type"], row["brand"], row["variant_id"]))
    validate(rows)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    family_counts = Counter(row["variant_family"] for row in rows)
    type_counts = Counter(row["manipulation_type"] for row in rows)
    print(f"Wrote {len(rows)} controlled variants to {output}")
    print("Families:", dict(sorted(family_counts.items())))
    print("Types:", dict(sorted(type_counts.items())))


if __name__ == "__main__":
    main()
