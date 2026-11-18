#!/usr/bin/env python3
"""Participant-level inferential analysis for PhishLens RQ3-RQ5."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "study/results/set1_participant_item_deidentified.csv",
    ROOT / "study/results/set2_participant_item_deidentified.csv",
    ROOT / "study/results/set3_participant_item_deidentified.csv",
]


def load_data() -> pd.DataFrame:
    frame = pd.concat([pd.read_csv(path, dtype=str).fillna("") for path in FILES], ignore_index=True).fillna("")
    frame["accuracy"] = frame["accuracy"].astype(int)
    if "analysis_status" not in frame:
        frame["analysis_status"] = "included"
    frame.loc[frame["analysis_status"] == "", "analysis_status"] = "included"
    return frame


def condition_model(frame: pd.DataFrame, phase: str) -> dict[str, object]:
    selected = frame[(frame["phase"] == phase) & (frame["analysis_status"] == "included")]
    participant = (
        selected.groupby(["participant_id", "condition", "set"], as_index=False)["accuracy"].mean()
    )
    model = smf.ols(
        "accuracy ~ C(condition, Treatment(reference='no_warning')) + C(set)",
        data=participant,
    ).fit(cov_type="HC3")
    result: dict[str, object] = {
        "participants": int(participant["participant_id"].nunique()),
        "condition_means": participant.groupby("condition")["accuracy"].mean().to_dict(),
        "terms": {},
    }
    for term in (
        "C(condition, Treatment(reference='no_warning'))[T.ai_explanation]",
        "C(condition, Treatment(reference='no_warning'))[T.standard_warning]",
    ):
        interval = model.conf_int().loc[term]
        result["terms"][term] = {
            "difference": float(model.params[term]),
            "ci_low": float(interval.iloc[0]),
            "ci_high": float(interval.iloc[1]),
            "p_value": float(model.pvalues[term]),
        }
    return result


def reliance_model(frame: pd.DataFrame) -> dict[str, object]:
    selected = frame[
        (frame["condition"] == "ai_explanation")
        & (frame["phase"] == "main")
        & (frame["analysis_status"] == "included")
        & (frame["ai_correctness"].isin(["correct", "incorrect"]))
    ].copy()
    selected["follow"] = (selected["participant_decision"] == selected["ai_verdict"]).astype(int)
    grouped = selected.groupby("ai_correctness").agg(
        decisions=("follow", "size"),
        followed=("follow", "sum"),
        follow_rate=("follow", "mean"),
        accurate=("accuracy", "sum"),
        accuracy=("accuracy", "mean"),
    )
    paired = selected.groupby(["participant_id", "ai_correctness"])["follow"].mean().unstack()
    difference = paired["incorrect"] - paired["correct"]
    t_result = stats.ttest_rel(paired["incorrect"], paired["correct"])
    w_result = stats.wilcoxon(paired["incorrect"], paired["correct"], zero_method="wilcox")
    interval = stats.t.interval(
        0.95,
        len(difference) - 1,
        loc=difference.mean(),
        scale=stats.sem(difference),
    )
    return {
        "descriptive": grouped.to_dict(orient="index"),
        "paired_participants": int(len(difference)),
        "incorrect_minus_correct_following": float(difference.mean()),
        "ci_low": float(interval[0]),
        "ci_high": float(interval[1]),
        "paired_t_p_value": float(t_result.pvalue),
        "wilcoxon_p_value": float(w_result.pvalue),
    }


def main() -> None:
    frame = load_data()
    output = {
        "rq3_main_accuracy": condition_model(frame, "main"),
        "rq4_ai_reliance": reliance_model(frame),
        "rq5_transfer_accuracy": condition_model(frame, "transfer"),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
