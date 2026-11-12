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
