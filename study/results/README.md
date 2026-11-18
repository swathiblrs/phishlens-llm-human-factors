# Human-study results

This directory contains aggregate, de-identified results from the PhishLens human study. Raw Google Forms exports, timestamps, and participant-level records are not stored in the repository.

## Set 1 preliminary summary

| Condition | Eligible participants | Main accuracy | Transfer accuracy | Mean confidence (1-3) | Mean trust (1-5) |
| --- | ---: | ---: | ---: | ---: | ---: |
| No warning | 9 | 53.7% | 60.0% | 2.23 | Not measured |
| Standard warning | 9 | 45.4% | 55.6% | 2.01 | 3.08 |
| AI explanation | 13 | 50.6% | 58.5% | 1.90 | 3.31 |

The AI-explanation export contained 14 submissions. One participant declined consent and was excluded, leaving 13 eligible responses. All eligible responses were complete. Forms A and B each contained nine eligible, complete responses.

These descriptive results are preliminary. The conditions have small, unequal sample sizes, so the differences should not be interpreted as statistically significant without the planned inferential analysis and the remaining form sets.

## Scoring

- Main-task accuracy uses 12 decisions per eligible participant.
- Transfer accuracy uses five unaided decisions per eligible participant.
- Decision confidence is coded as low = 1, medium = 2, and high = 3.
- Trust uses the form's 1-5 scale.
- Repeated Google Forms column labels were processed by column position to preserve each screenshot's responses.

See `set1_condition_summary.csv` for the machine-readable aggregate results.

Set 2 and Set 3 summaries are stored in their corresponding CSV files. See `combined_results_report.md` and `combined_condition_summary.csv` for the pooled three-set report.

## Research-question analysis

- `research_question_analysis.md` maps the currently supported findings and limitations to RQ1-RQ5.
- `team_action_plan.md` assigns the remaining data and evaluation work.
- `set1_form_mapping.csv` records the actual Set 1 item order and AI advice shown.
- `set1_participant_item_deidentified.csv` contains one de-identified row per eligible Set 1 participant and item. It excludes names, email addresses, timestamps, and age responses.
- `scripts/analyze_current_results.py` reproduces the current aggregate and reliance metrics.
- `scripts/build_set1_deidentified.py` rebuilds the Set 1 participant-item file from private form exports.
- `set3_form_mapping.csv` records the actual Set 3 item order and AI advice shown.
- `set3_participant_item_deidentified.csv` contains the privacy-safe Set 3 participant-item data.
- `scripts/build_set3_deidentified.py` rebuilds Set 3 from private exports supplied as command-line inputs.

Raw Set 3 Google Forms exports were removed from the current repository tree after de-identification. They remain in earlier Git history until that history is deliberately purged. Keep the repository private until the history is cleaned.
