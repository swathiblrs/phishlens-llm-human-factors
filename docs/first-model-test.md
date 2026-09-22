# First GPT, Claude, and Gemini screenshot test

Run this procedure only after the team receives an approved static screenshot and verifies its ground-truth label.

## Goal

Compare candidate multimodal models under the same input conditions. This first test checks the workflow; it is not a research result and should not be used to choose a model by itself.

## Required input

- One approved static screenshot
- A unique `sample_id`
- The displayed URL, or the literal value `unknown`
- A verified ground-truth label stored in `data/manifest.csv`
- Prompt version `phishing_analysis_v1`

Do not include the ground-truth label or modification type in the model prompt.

## Candidate models

- GPT candidate available to the team
- Claude candidate available to the team
- Gemini candidate available to the team

Record the exact model name and version shown by the provider at test time. Do not describe a generic web interface as a stable model version.

## Controlled procedure

1. Start a new conversation or session for each model.
2. Upload the exact same screenshot without resizing or editing it between models.
3. Copy the complete system instruction and researcher input from `prompts/phishing_analysis_v1.md`.
4. Replace only `SAMPLE_ID`, `DISPLAYED_URL_OR_UNKNOWN`, and neutral context.
5. Submit one request. Do not retry merely because the result is undesirable.
6. Save the complete unedited response under `results/raw/PROVIDER/SAMPLE_ID/`.
7. Record model name, displayed version, date, latency if available, and interface type.
8. Normalize the response into the JSON schema without changing its meaning.
9. Validate the normalized JSON:

   ```bash
   python3 scripts/validate_result.py path/to/result.json
   ```

10. Add one row to the processed CSV using the columns in `schemas/model_results_columns.csv`.

## If the model does not return valid JSON

Preserve the invalid raw response. Mark the run as a formatting failure. Do not silently repair or rerun it. Normalization may extract fields for analysis, but the raw response remains the authoritative record.

## Reproducibility notes

Free web interfaces may change models, prompts, or limits without notice. For the formal evaluation, use APIs or versioned endpoints if the team receives access. If manual interfaces remain necessary, document the interface, date, account tier, displayed model, and all observed limitations.
