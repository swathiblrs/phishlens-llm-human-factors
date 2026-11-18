# PhishLens Analysis Action Plan

## Immediate parallel work

### Swathi

- Maintain the canonical analysis script and research-question report.
- De-identify and convert Set 1 Forms A, B, and C into participant-by-item rows.
- Document the actual Set 1 item order, including the three items that differ from the shortlist CSV.
- After the technical-task decision, run the standardized ChatGPT evaluation.

### Prapti

- Set 2 responses and the item key are merged and de-identified.
- Questions 7 and 11 are documented form errors and are excluded from all three conditions in the primary analysis.
- Review the reconstructed exclusion note if the live form changed after export.
- After the technical-task decision, run the standardized Claude evaluation.

### Brigitte

- Set 3 exports, item mapping, and de-identification are complete.
- Review the reconstructed mapping if any screenshot was changed after the live form was created.
- After the technical-task decision, run the standardized Gemini evaluation.

## Team decisions

1. **Technical task:** Choose screenshot-plus-URL phishing detection or screenshot-only visual-anomaly detection. The recommended choice is screenshot-plus-URL because it matches the existing phishing research questions and the 167-row experiment manifest.
2. **Research-question numbering:** Use either four combined questions or the original five questions consistently across the paper, slides, and analysis. The current report uses five because it keeps incorrect-advice reliance and transfer learning separate.
3. **Uncertain advice:** Treat uncertain as incorrect for primary classification accuracy, while also reporting decision coverage and accuracy among binary decisions. Analyze participant reactions to uncertain advice as a separate exploratory category.
4. **Human-study mapping:** Confirm the actual screenshot order and model source in every live Form C rather than relying only on the shortlist CSV.
5. **Ethics record:** Confirm that the instructor reviewed the survey materials as required for the internal term project.

## Final analysis after exports arrive

- Create one de-identified long-form file with one row per participant and screenshot.
- Validate 12 main and five transfer decisions per eligible participant.
- Report results by set before pooling.
- Fit a mixed-effects logistic model with condition as a fixed effect and participant and screenshot as repeated sources of variation, if the final data support it.
- Measure appropriate reliance, overreliance, confidence calibration, trust, and unaided transfer.
- Preserve raw exports privately; commit only de-identified or aggregate research files.
