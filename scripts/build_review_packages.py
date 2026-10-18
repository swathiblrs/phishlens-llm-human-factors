#!/usr/bin/env python3
"""Create team-review packages with local screenshots and balanced assignments."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path


REVIEWERS = [
    "Swathi Bangalore Satish",
    "Prapti Bhatt",
    "Brigitte Turner",
]
PAIR_ROTATION = [(0, 1), (1, 2), (0, 2)]

COLUMNS = [
    "review_item_id",
    "split",
    "relative_image_path",
    "experiment_sample_ids",
    "context_pair_id",
    "brand",
    "variant_family",
    "manipulation_type",
    "manipulation_parameter",
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


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def image_key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["screenshot_path"], row["archive_path"], row["archive_member"]


def copy_image(repo_root: Path, source_row: dict[str, str], target: Path) -> None:
    if source_row["screenshot_path"]:
        source = (repo_root / source_row["screenshot_path"]).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, target)
        return

    archive = (repo_root / source_row["archive_path"]).resolve()
    if not archive.is_file():
        raise FileNotFoundError(archive)
    with zipfile.ZipFile(archive) as handle:
        try:
            data = handle.read(source_row["archive_member"])
        except KeyError as error:
            raise FileNotFoundError(source_row["archive_member"]) from error
    target.write_bytes(data)


def context_summary(rows: list[dict[str, str]]) -> str:
    ordered = sorted(rows, key=lambda row: row["context_type"])
    return " | ".join(
        f"{row['context_type']}: {row['displayed_url']} [{row['ground_truth']}]"
        for row in ordered
    )


def write_split(
    repo_root: Path,
    review_root: Path,
    split: str,
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    split_root = review_root / split
    screenshot_root = split_root / "screenshots"
    screenshot_root.mkdir(parents=True, exist_ok=True)

    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[image_key(row)].append(row)
    ordered_groups = sorted(
        groups.values(), key=lambda group: min(int(row["run_order"]) for row in group)
    )

    review_rows: list[dict[str, str]] = []
    for index, group in enumerate(ordered_groups, start=1):
        first = group[0]
        item_id = f"{split}-{index:03d}"
        descriptor = first["manipulation_type"] or "original"
        filename = f"{item_id}-{slug(first['brand'])}-{slug(descriptor)}.png"
        relative_image = Path("screenshots") / filename
        copy_image(repo_root, first, screenshot_root / filename)

        reviewer_indexes = PAIR_ROTATION[(index - 1) % len(PAIR_ROTATION)]
        review_rows.append(
            {
                "review_item_id": item_id,
                "split": split,
                "relative_image_path": relative_image.as_posix(),
                "experiment_sample_ids": " | ".join(
                    sorted(row["experiment_sample_id"] for row in group)
                ),
                "context_pair_id": first["context_pair_id"],
                "brand": first["brand"],
                "variant_family": first["variant_family"],
                "manipulation_type": first["manipulation_type"],
                "manipulation_parameter": first["manipulation_parameter"],
                "contexts_to_verify": context_summary(group),
                "assigned_reviewer_1": REVIEWERS[reviewer_indexes[0]],
                "assigned_reviewer_2": REVIEWERS[reviewer_indexes[1]],
                "reviewer_1_decision": "",
                "reviewer_1_notes": "",
                "reviewer_2_decision": "",
                "reviewer_2_notes": "",
                "disagreement": "",
                "final_status": "pending",
            }
        )

    output = split_root / f"{split}_review.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)
    return review_rows


def write_instructions(review_root: Path) -> None:
    instructions = """# Screenshot review instructions

Review only rows where your name appears in `assigned_reviewer_1` or
`assigned_reviewer_2`. Reviewers must work independently.

For every assigned row:

1. Open the file in `relative_image_path`.
2. Confirm that the image opens, is readable, and shows the listed brand.
3. For a controlled variant, confirm that the visible change matches
   `manipulation_type` and `manipulation_parameter`.
4. Check every entry in `contexts_to_verify`. Official-domain controls must use
   the brand's legitimate domain. Synthetic phishing contexts must use a `.test`
   domain. Never visit a displayed URL.
5. Confirm that the screenshot contains no personal or sensitive information.
6. Enter `approved`, `rejected`, or `needs_discussion` in your decision column.
7. Add a short note for every rejection or uncertainty.

Do not edit the other reviewer's decision. After both reviews are complete, set
`disagreement` to `no` when the decisions match or `yes` when they differ. For
matching decisions, copy the shared decision to `final_status`. When reviewers
disagree, discuss the screenshot as a team and record the agreed result in
`final_status`.

Review the pilot package first. Start the main package only after the team has
confirmed that the pilot procedure works. Keep transfer screenshots away from
future study participants until the unaided transfer task.
"""
    (review_root / "REVIEW_INSTRUCTIONS.md").write_text(
        instructions, encoding="utf-8"
    )


def validate(all_reviews: dict[str, list[dict[str, str]]], review_root: Path) -> None:
    expected = {"pilot": 9, "main": 96, "transfer": 5}
    actual = {split: len(rows) for split, rows in all_reviews.items()}
    if actual != expected:
        raise ValueError(f"Unexpected review counts: {actual}")

    assignment_counts = {reviewer: 0 for reviewer in REVIEWERS}
    ids: set[str] = set()
    for split, rows in all_reviews.items():
        for row in rows:
            if row["review_item_id"] in ids:
                raise ValueError(f"Duplicate review ID: {row['review_item_id']}")
            ids.add(row["review_item_id"])
            image = review_root / split / row["relative_image_path"]
            if not image.is_file() or image.stat().st_size == 0:
                raise ValueError(f"Missing review image: {image}")
            assignment_counts[row["assigned_reviewer_1"]] += 1
            assignment_counts[row["assigned_reviewer_2"]] += 1
    if sorted(assignment_counts.values()) != [73, 73, 74]:
        raise ValueError(f"Reviewer assignments are not balanced: {assignment_counts}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-manifest",
        type=Path,
        default=Path("data/experiment_subset.csv"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("review"))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    manifest = args.experiment_manifest if args.experiment_manifest.is_absolute() else repo_root / args.experiment_manifest
    review_root = args.output_root if args.output_root.is_absolute() else repo_root / args.output_root

    with manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    all_reviews: dict[str, list[dict[str, str]]] = {}
    for split in ("pilot", "main", "transfer"):
        all_reviews[split] = write_split(
            repo_root,
            review_root,
            split,
            [row for row in rows if row["split"] == split],
        )
    write_instructions(review_root)
    validate(all_reviews, review_root)

    print("Created review packages:")
    for split, review_rows in all_reviews.items():
        print(f"  {split}: {len(review_rows)} unique screenshots")


if __name__ == "__main__":
    main()
