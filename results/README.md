# Model evaluation results

Use one processed CSV per provider so ChatGPT, Claude, and Gemini results keep
the same columns without creating merge conflicts in a shared file.

## Processed result files

- `processed/chatgpt_results.csv`
- `processed/claude_results.csv`
- `processed/gemini_results.csv`
- `processed/sample_result.csv` contains one example row only. Do not include
  the example row in the final analysis.

Copy the model response into the provider's CSV using the exact existing
columns. Use one row per model run. Keep `evidence_json` as valid JSON inside a
single CSV cell. Record the exact displayed model name and version rather than
only the provider name.

## Raw responses

Store complete, unedited responses under the matching provider folder:

```text
raw/PROVIDER/SAMPLE_ID/response.json
```

Raw responses remain ignored by Git by default. Remove sensitive information
before changing that policy or sharing a response.

Use `phishing_analysis_v1` in `prompt_version`. Do not silently rerun or repair
an invalid response. Preserve it as a formatting failure and explain the issue
in `notes`.
