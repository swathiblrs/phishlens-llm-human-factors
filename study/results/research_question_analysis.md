# PhishLens Research-Question Analysis

## Status

This document separates findings supported by the current data from findings that still require additional data or a team decision. All results are preliminary until the participant-by-item dataset and standardized model runs are complete.

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
| No warning | 32 | 41.1% | 2.13/3 |
| Standard warning | 32 | 41.4% | 1.96/3 |
| AI explanation | 36 | 45.6% | 1.99/3 |

The pooled AI-explanation condition was 4.5 percentage points above no warning and 4.2 points above the standard warning. However, the pattern varied by screenshot set: AI versus no warning was -3.1 points in Set 1, +13.0 points in Set 2, and -4.9 points in Set 3. The pooled advantage is therefore driven primarily by Set 2 and should not yet be described as a general or statistically significant improvement.

## RQ4: How do users respond when an AI recommendation is incorrect?

Sets 1 and 3 provide a preliminary automation-bias signal. Each set's AI form contained four items with a definite phishing or legitimate AI verdict; the remaining eight were uncertain.

- Participants followed correct definite advice in 25 of 44 decisions (56.8%).
- Participants followed incorrect definite advice in 36 of 44 decisions (81.8%).
- Accuracy was 56.8% when definite advice was correct and 18.2% when it was incorrect.
- Mean trust was 2.98/5 for correct definite advice and 2.82/5 for incorrect definite advice.

This suggests possible overreliance on incorrect advice, but it is not conclusive. Set 2 item-level responses are not yet available, and two Set 2 AI explanations were attached to the wrong screenshots and must be excluded consistently from all three conditions. Set 1 and Set 3 mappings were reconstructed from the forms and validated against their published totals.

## RQ5: Do users who receive explanations perform better later without AI assistance?

| Condition | Transfer accuracy |
| --- | ---: |
| No warning | 55.6% |
| Standard warning | 56.3% |
| AI explanation | 60.6% |

The pooled AI-explanation group was 5.0 percentage points above no warning and 4.3 points above the standard warning. This is preliminary evidence of transfer, but the set-specific AI-versus-no-warning effects were -1.5 points in Set 1, +14.7 points in Set 2, and -5.6 points in Set 3. As with RQ3, Set 2 drives the pooled advantage.

## What is required for final answers

1. Obtain the Set 2 Forms A, B, and C exports and convert them to de-identified participant-by-item rows. Set 3 is complete.
2. Record the ordered screenshot mapping, model shown, model verdict, and advice correctness for every Form C item.
3. Analyze participant decisions while controlling for screenshot set, participant, and screenshot.
4. Decide whether Stage 1 is screenshot-plus-URL phishing detection or screenshot-only visual-anomaly detection.
5. If retaining phishing detection, rerun every model on the canonical 167 screenshot-plus-context inputs using the same prompt and metadata fields.
6. Code explanation quality with two reviewers, including grounded evidence, hallucination, URL reasoning, recommendation consistency, and misleading content.

## Reproducibility

Run `python3 scripts/analyze_current_results.py` from the repository root to reproduce the current RQ1, RQ2 response-profile, RQ3, and RQ5 aggregate calculations.
