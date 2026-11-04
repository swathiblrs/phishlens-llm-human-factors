#!/usr/bin/env python3
import csv
import os
from collections import defaultdict


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_FILE = os.path.join(ROOT, "review/main/main_review.csv")
RESULT_FILES = {
    "gpt": os.path.join(ROOT, "results/processed/chatgpt_results.csv"),
    "claude": os.path.join(ROOT, "results/processed/claude_results.csv"),
    "gemini": os.path.join(ROOT, "results/processed/gemini_results.csv"),
}
OUTPUT_DIR = os.path.join(ROOT, "study/stimuli")

LEGITIMATE_ORIGINALS = [
    "main-015-google-original",
    "main-016-wellsfargobank-original",
    "main-018-outlook-original",
    "main-025-bankofamerica-original",
    "main-042-capitalone-original",
    "main-052-tdbank-original",
    "main-060-paypal-original",
    "main-081-linkedin-original",
    "main-084-alibaba-original",
]

LEGITIMATE_CONTROLLED = [
    "main-001-adobe-scaling",
    "main-013-absabank-location-change",
    "main-019-instagram-cw",
    "main-026-bankofamerica-pgd",
    "main-032-dropbox-vit",
    "main-039-alibaba-resizing",
    "main-041-capitalone-pgd",
    "main-045-wellsfargobank-fgm",
    "main-068-absabank-color-change",
]

PHISHING_CONTROLLED = [
    "main-022-adobe-rotation",
    "main-023-absabank-omission",
    "main-038-apple-swin",
    "main-034-dropbox-srnet",
    "main-003-amazon-swin",
    "main-082-dhl-vit",
    "main-080-ebay-swin",
    "main-088-whatsapp-fgm",
    "main-079-facebook-cw",
]

PHISHING_ORIGINALS = [
    "main-004-alibaba-original",
    "main-017-instagram-original",
    "main-029-facebook-original",
    "main-035-adobe-original",
    "main-040-dhl-original",
    "main-046-amazon-original",
    "main-047-google-original",
    "main-051-ebay-original",
    "main-066-paypal-original",
]

PILOT_ITEMS = [
    ("pilot-006-netflix-original", "legitimate", "https://www.netflix.com/"),
    ("pilot-009-youtube-original", "legitimate", "https://www.youtube.com/"),
]

FIELDS = [
    "screenshot_id", "screenshot_path", "split", "brand", "displayed_url",
    "ground_truth", "variant_family", "manipulation_type",
    "gpt_verdict", "gpt_confidence", "gpt_recommended_action", "gpt_explanation", "gpt_correctness",
    "claude_verdict", "claude_confidence", "claude_recommended_action", "claude_explanation", "claude_correctness",
    "gemini_verdict", "gemini_confidence", "gemini_recommended_action", "gemini_explanation", "gemini_correctness",
    "inclusion_status", "notes",
]


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def result_index():
    output = {}
    for model, path in RESULT_FILES.items():
        by_stem = defaultdict(list)
        for row in read_rows(path):
            stem = os.path.splitext(os.path.basename(row["screenshot_path"]))[0]
            by_stem[stem].append(row)
        output[model] = by_stem
    return output


def correctness(verdict, ground_truth):
    verdict = (verdict or "").strip().lower()
    if verdict == ground_truth:
        return "correct"
    if verdict == "uncertain":
        return "uncertain"
    if not verdict:
        return "not_run"
    return "incorrect"


def extract_url(context, ground_truth):
    if "official_domain_control:" in context and ground_truth == "legitimate":
        return context.split("official_domain_control:", 1)[1].split(" [legitimate]", 1)[0].strip()
    if "synthetic_domain_mismatch:" in context and ground_truth == "phishing":
        return context.split("synthetic_domain_mismatch:", 1)[1].split(" [phishing]", 1)[0].strip()
    if "source_recorded:" in context:
        return context.split("source_recorded:", 1)[1].rsplit(" [", 1)[0].strip()
    raise ValueError(f"Could not extract {ground_truth} URL from: {context}")


def attach_model_fields(output, stem, ground_truth, results):
    for model in ("gpt", "claude", "gemini"):
        matches = results[model].get(stem, [])
        if len(matches) != 1:
            raise ValueError(f"Expected one {model} result for {stem}; found {len(matches)}")
        result = matches[0]
        output[f"{model}_verdict"] = result["verdict"].strip().lower()
        output[f"{model}_confidence"] = result["confidence"].strip()
        output[f"{model}_recommended_action"] = result["recommended_action"].strip()
        output[f"{model}_explanation"] = result["explanation"].strip()
        output[f"{model}_correctness"] = correctness(result["verdict"], ground_truth)


def build_main_row(review, ground_truth, results, note):
    stem = os.path.splitext(os.path.basename(review["relative_image_path"]))[0]
    output = {
        "screenshot_id": stem,
        "screenshot_path": f"review/main/{review['relative_image_path']}",
        "split": "main",
        "brand": review["brand"].strip(),
        "displayed_url": extract_url(review["contexts_to_verify"], ground_truth),
        "ground_truth": ground_truth,
        "variant_family": review["variant_family"].strip(),
        "manipulation_type": review["manipulation_type"].strip(),
        "inclusion_status": "selected",
        "notes": note,
    }
    attach_model_fields(output, stem, ground_truth, results)
    return output


def build_pilot_row(stem, ground_truth, displayed_url, results):
    brand = stem.split("-", 3)[2]
    output = {
        "screenshot_id": stem,
        "screenshot_path": f"review/pilot/screenshots/{stem}.png",
        "split": "pilot",
        "brand": brand,
        "displayed_url": displayed_url,
        "ground_truth": ground_truth,
        "variant_family": "original",
        "manipulation_type": "original",
        "inclusion_status": "pilot_only",
        "notes": "Reserved for form and procedure testing; exclude from final-study analysis.",
    }
    attach_model_fields(output, stem, ground_truth, results)
    return output


def write_csv(name, rows):
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    review_by_stem = {}
    for row in read_rows(REVIEW_FILE):
        stem = os.path.splitext(os.path.basename(row["relative_image_path"]))[0]
        review_by_stem[stem] = row
    results = result_index()

    legitimate_rows = [
        build_main_row(review_by_stem[stem], "legitimate", results, "Original legitimate control selected by Brigitte.")
        for stem in LEGITIMATE_ORIGINALS
    ]
    legitimate_rows += [
        build_main_row(review_by_stem[stem], "legitimate", results, "Controlled legitimate variant added during shortlist completion.")
        for stem in LEGITIMATE_CONTROLLED
    ]

    phishing_rows = [
        build_main_row(review_by_stem[stem], "phishing", results, "Controlled phishing-context candidate selected by Prapti.")
        for stem in PHISHING_CONTROLLED
    ]
    phishing_rows += [
        build_main_row(review_by_stem[stem], "phishing", results, "Original phishing example added during shortlist completion.")
        for stem in PHISHING_ORIGINALS
    ]

    pilot_rows = [build_pilot_row(stem, truth, url, results) for stem, truth, url in PILOT_ITEMS]

    write_csv("shortlisted_legitimate.csv", legitimate_rows)
    write_csv("shortlisted_phishing.csv", phishing_rows)
    write_csv("shortlisted_pilot.csv", pilot_rows)


if __name__ == "__main__":
    main()
