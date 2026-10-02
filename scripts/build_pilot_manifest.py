#!/usr/bin/env python3
"""Build a deterministic, brand-matched PhishLens pilot manifest.

The script does not copy screenshots and never opens a URL. It selects one
legitimate and one full-size phishing screenshot for each configured brand.
"""

from __future__ import annotations

import argparse
import csv
import re
import struct
from pathlib import Path


SELECTED_BRANDS = [
    "facebook",
    "instagram",
    "linkedin",
    "whatsapp",
    "paypal",
    "WellsFargoBank",
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
    "ChronopostInternational",
    "netflix",
    "spotify",
    "youtube",
    "steam",
    "att",
    "orange",
    "godaddy",
    "yahoo",
    "webmail",
]

MANIFEST_COLUMNS = [
    "sample_id",
    "ground_truth",
    "screenshot_path",
    "displayed_url",
    "source_type",
    "source_reference",
    "parent_sample_id",
    "modification_type",
    "modification_description",
    "reviewer_1",
    "reviewer_2",
    "label_agreement",
    "notes",
]

SOURCE_REFERENCE = (
    "Ji et al., USENIX Security 2025; "
    "https://moa-lab.net/evaluation-visual-similarity-based-phishing-detection-models/"
)


def normalize_brand(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def repo_relative_path(path: Path, repo_root: Path) -> str:
    """Return a portable relative path from the repository root."""
    import os

    return os.path.relpath(path.resolve(), repo_root.resolve())


def image_is_usable(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            signature = handle.read(24)
        if len(signature) != 24 or signature[:8] != b"\x89PNG\r\n\x1a\n":
            return False
        width, height = struct.unpack(">II", signature[16:24])
        return width >= 640 and height >= 480
    except OSError:
        return False


def resolve_phishing_path(root: Path, stored_path: str) -> Path:
    candidates = [
        Path(stored_path),
        root / stored_path,
        root / "apwg_sample_4190" / stored_path,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(stored_path)


def read_phishing_rows(phishing_root: Path) -> dict[str, list[dict[str, str]]]:
    csv_path = phishing_root / "phishing4190_2.csv"
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    by_brand: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_brand.setdefault(normalize_brand(row["brand"]), []).append(row)

    for brand_rows in by_brand.values():
        brand_rows.sort(key=lambda row: row["scr_path"])
    return by_brand


def choose_phishing_row(
    phishing_root: Path, candidates: list[dict[str, str]]
) -> tuple[dict[str, str], Path]:
    for row in candidates:
        screenshot = resolve_phishing_path(phishing_root, row["scr_path"])
        if image_is_usable(screenshot):
            return row, screenshot
    raise ValueError("No screenshot at least 640x480 was available for this brand")


def build_manifest(
    repo_root: Path, benign_root: Path, phishing_root: Path
) -> list[dict[str, str]]:
    phishing_by_brand = read_phishing_rows(phishing_root)
    rows: list[dict[str, str]] = []

    for index, benign_brand in enumerate(SELECTED_BRANDS, start=1):
        normalized = normalize_brand(benign_brand)
        benign_dir = benign_root / benign_brand
        benign_screenshot = benign_dir / "login.png"
        benign_url_file = benign_dir / "login.txt"

        if not benign_screenshot.is_file() or not benign_url_file.is_file():
            raise FileNotFoundError(f"Incomplete benign sample: {benign_dir}")
        if normalized not in phishing_by_brand:
            raise ValueError(f"No phishing rows match benign brand {benign_brand}")

        phishing_row, phishing_screenshot = choose_phishing_row(
            phishing_root, phishing_by_brand[normalized]
        )
        benign_url = benign_url_file.read_text(encoding="utf-8", errors="replace").strip()
        pair_id = f"pair-{index:02d}-{normalized}"

        rows.append(
            {
                "sample_id": f"legit-{index:02d}-{normalized}",
                "ground_truth": "legitimate",
                "screenshot_path": repo_relative_path(benign_screenshot, repo_root),
                "displayed_url": benign_url,
                "source_type": "crawl_benign",
                "source_reference": SOURCE_REFERENCE,
                "parent_sample_id": "",
                "modification_type": "original",
                "modification_description": "Unmodified legitimate reference screenshot",
                "reviewer_1": "",
                "reviewer_2": "",
                "label_agreement": "pending",
                "notes": f"Matched brand pair {pair_id}; brand={benign_brand}",
            }
        )
        rows.append(
            {
                "sample_id": f"phish-{index:02d}-{normalized}",
                "ground_truth": "phishing",
                "screenshot_path": repo_relative_path(phishing_screenshot, repo_root),
                "displayed_url": phishing_row["domain"].strip(),
                "source_type": "phishing4190",
                "source_reference": SOURCE_REFERENCE,
                "parent_sample_id": "",
                "modification_type": "original",
                "modification_description": "Unmodified APWG phishing screenshot",
                "reviewer_1": "",
                "reviewer_2": "",
                "label_agreement": "pending",
                "notes": (
                    f"Matched brand pair {pair_id}; "
                    f"brand={phishing_row['brand'].strip()}; minimum resolution 640x480"
                ),
            }
        )

    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benign-root", type=Path, required=True)
    parser.add_argument("--phishing-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/manifest.csv"))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else repo_root / args.output
    rows = build_manifest(repo_root, args.benign_root, args.phishing_root)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=MANIFEST_COLUMNS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} samples to {output}")
    print("30 legitimate + 30 phishing, matched across 30 brands")


if __name__ == "__main__":
    main()
