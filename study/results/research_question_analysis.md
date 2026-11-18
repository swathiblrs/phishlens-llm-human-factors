# PhishLens Research-Question Analysis

## Status

This document separates findings supported by the current data from findings that still require a technical-design decision. De-identified participant-item data are available for all three human-study sets. Standardized model runs are not yet complete.

| Research question | Current status | Current answer |
| --- | --- | --- |
| RQ1: Model accuracy | Partially answered | Original screenshots can be compared; controlled URL contexts are incomplete. |
| RQ2: Manipulation failures | Partially answered | Response patterns are available, but classification accuracy and explanation coding are incomplete. |
| RQ3: User accuracy | Answered | AI explanations produced a modest, non-significant improvement. |
| RQ4: Incorrect AI advice | Answered | Participants followed incorrect advice significantly more often than correct advice. |
| RQ5: Unaided transfer | Answered | The AI group scored higher descriptively, but the improvement was not statistically significant. |

## RQ1: How accurately do multimodal LLMs distinguish phishing and legitimate websites?

The defensible current comparison uses the balanced 42-image main-original subset: 21 legitimate and 21 phishing screenshots. These images have unambiguous screenshot-level labels, and all three models evaluated them without a displayed URL.

| Model | Correct | Accuracy | Binary-decision coverage | Accuracy when binary |
| --- | ---: | ---: | ---: | ---: |
| Claude | 31/42 | 73.8% | 97.6% | 75.6% |
| ChatGPT | 6/42 | 14.3% | 14.3% | 100.0% |
| Gemini | 6/42 | 14.3% | 14.3% | 100.0% |

Claude classified all 21 legitimate originals correctly, but detected only 10 of 21 phishing originals. It mislabeled 10 phishing originals as legitimate and returned uncertain once. ChatGPT and Gemini each detected six phishing originals and returned uncertain for the other 36 items, including every legitimate original.

This is not a final model leaderboard. Claude's exact prompt version was not recorded, and the broader pilot inputs were not presented consistently across models.

## RQ2: Which visual manipulations cause classification or explanation failures?

The 54 main controlled screenshots cannot currently be scored as correct or incorrect because each image has two intended URL contexts: an official-domain context labeled legitimate and a synthetic-domain context labeled phishing. None of the three model runs included those URLs for these items.

The current runs support only an exploratory response-profile analysis:

- ChatGPT returned uncertain for 53 of 54 controlled screenshots and phishing for one replacement example.
- Gemini returned uncertain for 52 of 54, phishing for one replacement example, and phishing for one integration example.
- Claude returned 28 uncertain, 15 legitimate, and 11 phishing judgments.
- Claude flagged every flipping, integration, and SRNet example as phishing (nine of nine total) and two of three replacement examples.
- Claude labeled every blur and rotation example legitimate (six of six total), despite the controlled visual changes.

Each manipulation has only three main screenshots, so these patterns are exploratory. A final RQ2 answer requires the same models to evaluate both URL contexts or requires the research question to be changed to visual-anomaly detection.

## RQ3: Do AI explanations improve user accuracy relative to a warning or no warning?

Across Sets 1–3:

| Condition | Eligible participants | Main accuracy | Mean confidence |
| --- | ---: | ---: | ---: |
| No warning | 32 | 43.5% | 2.12/3 |
| Standard warning | 32 | 43.8% | 1.96/3 |
| AI explanation | 36 | 48.8% | 1.94/3 |

The pooled AI-explanation condition was 5.3 percentage points above no warning and 5.0 points above the standard warning. After adjusting participant-level accuracy for screenshot set, the AI-versus-no-warning difference was 5.8 points (95% CI -1.8 to 13.4, p=0.135). Standard warning versus no warning was 0.8 points (p=0.846). AI explanations therefore showed a modest descriptive improvement, but not a statistically significant one.

The pattern varied by set: AI versus no warning was -3.1 points in Set 1, +18.3 points in corrected Set 2, and -4.9 points in Set 3. The pooled advantage is driven by Set 2. Set 2 questions 7 and 11 are excluded from every condition because Form C displayed explanations for different screenshots; the original 12-item result is retained as a sensitivity analysis.

## RQ4: How do users respond when an AI recommendation is incorrect?

All three sets provide an automation-bias result. Set 2 questions 7 and 11 are excluded because their AI text belonged to different screenshots.

- Participants followed correct definite advice in 61 of 86 decisions (70.9%).
- Participants followed incorrect definite advice in 63 of 72 decisions (87.5%).
- Accuracy was 70.9% when definite advice was correct and 12.5% when it was incorrect.
- Mean trust was 3.50/5 for correct definite advice and 3.35/5 for incorrect definite advice.

At the participant level, the mean incorrect-minus-correct following difference was 19.4 percentage points (95% CI 7.3 to 31.6). A paired test was statistically significant (paired t-test p=0.0026; Wilcoxon p=0.0084). This supports the conclusion that participants over-relied on incorrect definite AI advice.

## RQ5: Do users who receive explanations perform better later without AI assistance?

| Condition | Transfer accuracy |
| --- | ---: |
| No warning | 55.6% |
| Standard warning | 56.3% |
| AI explanation | 60.6% |

The pooled AI-explanation group was 5.0 percentage points above no warning and 4.3 points above the standard warning. After adjusting participant-level transfer accuracy for set, the AI-versus-no-warning difference was 4.5 points (95% CI -4.0 to 13.1, p=0.302). Standard warning versus no warning was 0.6 points (p=0.886). The data therefore do not provide statistically significant evidence of later unaided learning.

## What is required for final answers

1. Decide whether Stage 1 is screenshot-plus-URL phishing detection or screenshot-only visual-anomaly detection.
2. If retaining phishing detection, rerun every model on the canonical 167 screenshot-plus-context inputs using the same prompt and metadata fields.
3. Code explanation quality with two reviewers, including grounded evidence, hallucination, URL reasoning, recommendation consistency, and misleading content.
4. Run the final item-level mixed-effects model as a robustness analysis for RQ3 and RQ5.

## Reproducibility

Run `python3 scripts/analyze_current_results.py` from the repository root to reproduce the current RQ1, RQ2 response-profile, RQ3, and RQ5 aggregate calculations.
