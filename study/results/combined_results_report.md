# PhishLens Human-Study Results Report

## Repository update

Two additional result summaries were merged after the Set 1 report:

- Set 2 summary: commit `d714d6f`
- Set 3 summary: commit `54892e6`

The repository now contains aggregate results for Sets 1, 2, and 3. This report combines those files. It does not include raw responses, email addresses, timestamps, or participant-level records.

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
| No warning | 158/384 | 41.1% | 89/160 | 55.6% | 2.13 | Not measured |
| Standard warning | 159/384 | 41.4% | 90/160 | 56.3% | 1.96 | 3.29 |
| AI explanation | 197/432 | 45.6% | 109/180 | 60.6% | 1.99 | 3.35 |

Across all three conditions, participants made 1,200 main-task decisions and 500 transfer decisions. Overall accuracy was 42.8% for the main task and 57.6% for the transfer task.

## Preliminary observations

- The AI-explanation condition had the highest pooled main-task accuracy at 45.6%.
- Main-task accuracy in the standard-warning condition, 41.4%, was nearly the same as the no-warning condition, 41.1%.
- The AI-explanation condition also had the highest transfer accuracy at 60.6%.
- Average trust was slightly higher for AI explanations, 3.35 out of 5, than for standard warnings, 3.29 out of 5.
- Average confidence was highest without a warning, even though this condition did not have the highest accuracy. This may be relevant to confidence calibration.

## Interpretation limits

These are descriptive, pooled results. The conditions have unequal eligible sample sizes, and the three screenshot sets differ in difficulty. The differences should not be described as statistically significant until participant-level data are analyzed with methods that account for both participant and screenshot effects. The summary files are sufficient for progress reporting, but not for the final inferential analysis.

## Source files

- `set1_condition_summary.csv`
- `set2_condition_summary.csv`
- `set3_condition_summary.csv`
