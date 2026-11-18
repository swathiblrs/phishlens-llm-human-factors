# PhishLens Analysis Action Plan

## Immediate parallel work

### Swathi

- Maintain the canonical analysis script and research-question report.
- De-identify and convert Set 1 Forms A, B, and C into participant-by-item rows.
- Document the actual Set 1 item order, including the three items that differ from the shortlist CSV.
- Update the paper and slides with the finalized screenshot-only RQ1-RQ2 wording and results.

### Prapti

- Set 2 responses and the item key are merged and de-identified.
- Questions 7 and 11 are documented form errors and are excluded from all three conditions in the primary analysis.
- Review the reconstructed exclusion note if the live form changed after export.
- Verify the Set 2 exclusion description and review the screenshot-only technical summary.

### Brigitte

- Set 3 exports, item mapping, and de-identification are complete.
- Review the reconstructed mapping if any screenshot was changed after the live form was created.
- Review the screenshot-only manipulation table and confirm the reported model outputs.

## Finalized analysis choices

1. **Technical task:** Use screenshot-only model judgment and visual-manipulation sensitivity. Do not assign URL-dependent labels to controlled screenshots and do not run the 501 URL-context evaluations.
2. **Research-question numbering:** Use either four combined questions or the original five questions consistently across the paper, slides, and analysis. The current report uses five because it keeps incorrect-advice reliance and transfer learning separate.
3. **Uncertain advice:** Treat uncertain as incorrect for primary classification accuracy, while also reporting decision coverage and accuracy among binary decisions. Analyze participant reactions to uncertain advice as a separate exploratory category.
4. **Human-study mapping:** Confirm the actual screenshot order and model source in every live Form C rather than relying only on the shortlist CSV.
5. **Ethics record:** Confirm that the instructor reviewed the survey materials as required for the internal term project.

## Final reporting work

- Report results by set before pooling.
- Run an item-level mixed-effects robustness model if it converges.
- Update the paper's Methods, Results, Discussion, and Limitations with the corrected study design.
- Preserve raw exports privately; commit only de-identified or aggregate research files.
