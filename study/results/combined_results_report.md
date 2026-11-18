# PhishLens Human-Study Results Report

## Repository update

Two additional result summaries were merged after the Set 1 report:

- Set 2 summary: commit `d714d6f`
- Set 3 summary: commit `54892e6`

The repository now contains aggregate and de-identified participant-item results for Sets 1, 2, and 3. This report combines those files. It does not include names, email addresses, timestamps, ages, or free-text comments.

## Response totals

| Condition | Submitted | Eligible | Declined |
| --- | ---: | ---: | ---: |
| No warning | 32 | 32 | 0 |
| Standard warning | 32 | 32 | 0 |
| AI explanation | 38 | 36 | 2 |
| **Total** | **102** | **100** | **2** |

## Combined results

Results are pooled across Sets 1, 2, and 3. Accuracy is calculated from the total number of correct decisions divided by the total number of decisions. Confidence and trust are weighted by the number of main-task decisions in each set.

| Condition | Main correct | Main accuracy | Transfer correct | Transfer accuracy | Mean confidence (1–3) | Mean trust (1–5) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| No warning | 154/354 | 43.5% | 89/160 | 55.6% | 2.12 | Not measured |
| Standard warning | 155/354 | 43.8% | 90/160 | 56.3% | 1.96 | 3.29 |
| AI explanation | 197/404 | 48.8% | 109/180 | 60.6% | 1.94 | 3.30 |

Across all three conditions, participants contributed 1,112 included main-task decisions and 500 transfer decisions. Overall accuracy was 45.5% for the included main task and 57.6% for the transfer task. Set 2 questions 7 and 11 were excluded from all conditions because Form C displayed AI explanations belonging to different screenshots. The original 12-item Set 2 results are retained as a sensitivity analysis.

## Preliminary observations

- The AI-explanation condition had the highest pooled main-task accuracy at 48.8%.
- Main-task accuracy in the standard-warning condition, 43.8%, was nearly the same as the no-warning condition, 43.5%.
- The AI-explanation condition also had the highest transfer accuracy at 60.6%.
- Average trust was similar for AI explanations, 3.30 out of 5, and standard warnings, 3.29 out of 5.
- Average confidence was highest without a warning, even though this condition did not have the highest accuracy. This may be relevant to confidence calibration.

## Interpretation limits

Participant-level accuracy models adjusted for screenshot set found no statistically significant main-task advantage for AI explanations over no warning: adjusted difference 5.8 percentage points, 95% CI -1.8 to 13.4, p=0.135. The transfer difference was also not statistically significant: adjusted difference 4.5 points, 95% CI -4.0 to 13.1, p=0.302. These models use one accuracy score per participant and adjust for set; a final mixed-effects item-level model can additionally account for screenshot variation.

## Source files

- `set1_condition_summary.csv`
- `set2_condition_summary.csv`
- `set3_condition_summary.csv`
