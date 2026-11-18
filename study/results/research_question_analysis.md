# PhishLens Research-Question Analysis

## Status

This document reports the screenshot-only technical evaluation and the three-condition human study. De-identified participant-item data are available for all three human-study sets. The technical analysis uses only the screenshot evidence supplied to each model and does not assign URL-dependent phishing labels to controlled variants.

| Research question | Current status | Current answer |
| --- | --- | --- |
| RQ1: Screenshot-only model judgment | Answered | Original-page accuracy, abstention, and controlled-page judgment behavior are reported. |
| RQ2: Manipulation sensitivity | Answered descriptively | Judgment distributions are reported for all 18 manipulation types. |
| RQ3: User accuracy | Answered | AI explanations produced a modest, non-significant improvement. |
| RQ4: Incorrect AI advice | Answered | Participants followed incorrect advice significantly more often than correct advice. |
| RQ5: Unaided transfer | Answered | The AI group scored higher descriptively, but the improvement was not statistically significant. |

## RQ1: How do multimodal LLMs judge original and visually manipulated website screenshots without URL context?

The defensible current comparison uses the balanced 42-image main-original subset: 21 legitimate and 21 phishing screenshots. These images have unambiguous screenshot-level labels, and all three models evaluated them without a displayed URL.

| Model | Correct | Accuracy | Binary-decision coverage | Accuracy when binary |
| --- | ---: | ---: | ---: | ---: |
| Claude | 31/42 | 73.8% | 97.6% | 75.6% |
| ChatGPT | 6/42 | 14.3% | 14.3% | 100.0% |
| Gemini | 6/42 | 14.3% | 14.3% | 100.0% |

Claude classified all 21 legitimate originals correctly, but detected only 10 of 21 phishing originals. It mislabeled 10 phishing originals as legitimate and returned uncertain once. ChatGPT and Gemini each detected six phishing originals and returned uncertain for the other 36 items, including every legitimate original.

For the 54 controlled main screenshots, ChatGPT returned 53 uncertain and one phishing judgment; Gemini returned 52 uncertain and two phishing judgments; Claude returned 28 uncertain, 11 phishing, and 15 legitimate judgments. Treating phishing or uncertain as a cautious response, the cautious-response rate was 100% for ChatGPT and Gemini and 72.2% for Claude. This is judgment behavior, not URL-aware phishing accuracy.

Claude produced substantially more binary decisions on original screenshots. ChatGPT and Gemini mostly abstained. This comparison should not be presented as a definitive model leaderboard because Claude's exact prompt version was not recorded.

## RQ2: Which manipulation types most often produce phishing, legitimate, or uncertain judgments?

The screenshot-only analysis reports response sensitivity rather than URL-dependent phishing accuracy:

- ChatGPT returned uncertain for 53 of 54 controlled screenshots and phishing for one replacement example.
- Gemini returned uncertain for 52 of 54, phishing for one replacement example, and phishing for one integration example.
- Claude returned 28 uncertain, 15 legitimate, and 11 phishing judgments.
- Claude flagged every flipping, integration, and SRNet example as phishing (nine of nine total) and two of three replacement examples.
- Claude labeled every blur and rotation example legitimate (six of six total), despite the controlled visual changes.

Claude was most sensitive to flipping, integration, SRNet, and replacement. Blur and rotation were the clearest misses for Claude because all six examples received legitimate judgments. ChatGPT and Gemini avoided legitimate judgments but relied heavily on uncertain responses. Each manipulation has only three screenshots, so the manipulation comparison is descriptive and should not be generalized beyond this dataset.

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

## Remaining robustness and reporting work

1. Run the final item-level mixed-effects model as a robustness analysis for RQ3 and RQ5.
2. If the paper makes explanation-quality claims beyond participant reliance, code grounded evidence, hallucination, and misleading content with two reviewers.
3. Update the paper and slides so RQ1-RQ2 consistently describe screenshot-only judgment and manipulation sensitivity, not URL-aware phishing accuracy.

## Reproducibility

Run `python3 scripts/analyze_current_results.py` from the repository root to reproduce the current RQ1, RQ2 response-profile, RQ3, and RQ5 aggregate calculations.
