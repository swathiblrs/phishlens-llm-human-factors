#!/usr/bin/env python3
"""Reproduce the currently defensible PhishLens summary statistics.

This analysis deliberately separates unambiguous original screenshots from
controlled screenshots whose phishing label depends on the displayed URL.
It does not modify source data.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_FILES = {
    "chatgpt": ROOT / "results/processed/chatgpt_results.csv",
    "claude": ROOT / "results/processed/claude_results.csv",
    "gemini": ROOT / "results/processed/gemini_results.csv",
}
HUMAN_FILES = sorted((ROOT / "study/results").glob("set[123]_condition_summary.csv"))
SET1_ITEM_FILE = ROOT / "study/results/set1_participant_item_deidentified.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_verdict(value: str) -> str:
    verdict = value.strip().lower()
    if verdict == "suspicious":
        return "uncertain"
    return verdict


def canonical_main_original_truth() -> dict[str, str]:
    """Use the two agreeing files only to identify the balanced main originals.

    The model verdicts are never used as ground truth. ChatGPT and Claude store
    the same 21 legitimate and 21 phishing source labels for these originals.
    Gemini's recorded ground-truth column is known to be incorrect and is not
    used.
    """

    sources = [read_csv(MODEL_FILES["chatgpt"]), read_csv(MODEL_FILES["claude"])]
    maps = []
    for rows in sources:
        maps.append(
            {
                row["screenshot_path"]: row["ground_truth"]
                for row in rows
                if "review/main/" in row["screenshot_path"]
                and row["modification_type"] == "original"
            }
        )
    assert maps[0] == maps[1], "ChatGPT and Claude main-original labels disagree"
    assert len(maps[0]) == 42, "Expected 42 main original screenshots"
    assert Counter(maps[0].values()) == {"legitimate": 21, "phishing": 21}
    return maps[0]


def model_metrics() -> dict[str, object]:
    truth = canonical_main_original_truth()
    output: dict[str, object] = {}

    for model, path in MODEL_FILES.items():
        by_path = {
            row["screenshot_path"]: row
            for row in read_csv(path)
            if row["screenshot_path"] in truth
        }
        assert set(by_path) == set(truth), f"{model} is missing main originals"
        verdicts = {key: normalize_verdict(row["verdict"]) for key, row in by_path.items()}
        decisive = [key for key, verdict in verdicts.items() if verdict in {"legitimate", "phishing"}]
        correct = [key for key, verdict in verdicts.items() if verdict == truth[key]]
        selective_correct = [key for key in decisive if verdicts[key] == truth[key]]

        classes = {}
        for label in ("legitimate", "phishing"):
            keys = [key for key, value in truth.items() if value == label]
            classes[label] = {
                "correct": sum(verdicts[key] == label for key in keys),
                "total": len(keys),
                "verdicts": dict(Counter(verdicts[key] for key in keys)),
            }

        output[model] = {
            "correct": len(correct),
            "total": len(truth),
            "accuracy": len(correct) / len(truth),
            "binary_decisions": len(decisive),
            "binary_decision_coverage": len(decisive) / len(truth),
            "selective_accuracy": len(selective_correct) / len(decisive) if decisive else None,
            "by_ground_truth": classes,
        }

    return output


def manipulation_profiles() -> dict[str, object]:
    chatgpt_rows = read_csv(MODEL_FILES["chatgpt"])
    controlled_paths = {
        row["screenshot_path"]: row["modification_type"]
        for row in chatgpt_rows
        if "review/main/" in row["screenshot_path"] and row["modification_type"] != "original"
    }
    assert len(controlled_paths) == 54, "Expected 54 main controlled screenshots"

    profiles: dict[str, object] = {}
    for model, path in MODEL_FILES.items():
        rows = {
            row["screenshot_path"]: row
            for row in read_csv(path)
            if row["screenshot_path"] in controlled_paths
        }
        assert set(rows) == set(controlled_paths), f"{model} is missing controlled screenshots"
        by_type: dict[str, Counter[str]] = defaultdict(Counter)
        overall: Counter[str] = Counter()
        for screenshot_path, modification in controlled_paths.items():
            verdict = normalize_verdict(rows[screenshot_path]["verdict"])
            by_type[modification][verdict] += 1
            overall[verdict] += 1
        profiles[model] = {
            "overall": dict(overall),
            "by_manipulation": {key: dict(value) for key, value in sorted(by_type.items())},
        }
    return profiles


def human_metrics() -> dict[str, object]:
    rows = [row for path in HUMAN_FILES for row in read_csv(path)]
    assert len(rows) == 9, "Expected three conditions in each of three sets"
    output: dict[str, object] = {}
    for condition in ("no_warning", "standard_warning", "ai_explanation"):
        selected = [row for row in rows if row["condition"] == condition]
        main_correct = sum(int(row["main_correct"]) for row in selected)
        main_decisions = sum(int(row["main_decisions"]) for row in selected)
        transfer_correct = sum(int(row["transfer_correct"]) for row in selected)
        transfer_decisions = sum(int(row["transfer_decisions"]) for row in selected)
        confidence = sum(
            float(row["mean_decision_confidence_1_to_3"]) * int(row["main_decisions"])
            for row in selected
        ) / main_decisions
        trust_rows = [row for row in selected if row["mean_trust_1_to_5"]]
        trust = None
        if trust_rows:
            trust = sum(
                float(row["mean_trust_1_to_5"]) * int(row["main_decisions"])
                for row in trust_rows
            ) / sum(int(row["main_decisions"]) for row in trust_rows)
        output[condition] = {
            "submitted": sum(int(row["submitted_responses"]) for row in selected),
            "eligible": sum(int(row["eligible_responses"]) for row in selected),
            "declined": sum(int(row["declined_responses"]) for row in selected),
            "main_correct": main_correct,
            "main_decisions": main_decisions,
            "main_accuracy": main_correct / main_decisions,
            "transfer_correct": transfer_correct,
            "transfer_decisions": transfer_decisions,
            "transfer_accuracy": transfer_correct / transfer_decisions,
            "mean_confidence": confidence,
            "mean_trust": trust,
        }
    return output


def set1_reliance_metrics() -> dict[str, object]:
    rows = [
        row
        for row in read_csv(SET1_ITEM_FILE)
        if row["condition"] == "ai_explanation"
        and row["phase"] == "main"
        and row["ai_correctness"] in {"correct", "incorrect"}
    ]
    output: dict[str, object] = {}
    for advice_status in ("correct", "incorrect"):
        selected = [row for row in rows if row["ai_correctness"] == advice_status]
        followed = sum(row["participant_decision"] == row["ai_verdict"] for row in selected)
        accurate = sum(int(row["accuracy"]) for row in selected)
        trust = [float(row["trust"]) for row in selected if row["trust"]]
        output[advice_status] = {
            "decisions": len(selected),
            "followed": followed,
            "follow_rate": followed / len(selected),
            "accurate": accurate,
            "accuracy": accurate / len(selected),
            "mean_trust": sum(trust) / len(trust),
        }
    return output


def main() -> None:
    report = {
        "model_main_originals": model_metrics(),
        "main_controlled_response_profiles": manipulation_profiles(),
        "human_study": human_metrics(),
        "set1_definite_ai_advice": set1_reliance_metrics(),
        "limitations": [
            "Controlled screenshots are context-dependent when the displayed URL is hidden.",
            "Model prompts and URL availability were not identical across providers.",
            "Human-study inferential tests require de-identified participant-by-item data.",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
