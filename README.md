# PhishLens

Human-centered evaluation of multimodal LLM detection and explanations for visually manipulated phishing websites.

## Research objective

PhishLens uses a two-stage methodology:

1. **LLM evaluation:** Test how controlled visual modifications affect multimodal LLM classifications and evidence-based explanations.
2. **Human study:** Use selected correct and incorrect LLM outputs as study stimuli to measure user accuracy, trust, reliance, and learning.

This repository does not train a new LLM. It provides the dataset conventions, standard prompt, output schemas, evaluation code, and study materials needed to evaluate existing multimodal models reproducibly.

## Current status

- Repository structure: ready
- Standard multimodal prompt: ready
- JSON and CSV output formats: ready
- Output validator and tests: ready
- Dataset: awaiting professor-approved screenshots
- First GPT, Claude, and Gemini comparison: awaiting the first approved screenshot
- Human study: design stage; no participant data has been collected

## Repository structure

```text
phishlens-llm-human-factors/
├── analysis/                 Statistical analysis code and notebooks
├── data/
│   ├── original/             Approved original screenshots (not committed by default)
│   ├── perturbed/            Controlled visual modifications (not committed by default)
│   └── manifest.csv          Dataset metadata template
├── docs/                     Research and testing documentation
├── paper/                    Report drafts and figures
├── presentation/             Proposal and final-presentation material
├── prompts/                  Versioned LLM prompts
├── results/
│   ├── raw/                  Unmodified model responses
│   └── processed/            Validated, normalized results
├── schemas/                  JSON and CSV specifications
├── scripts/                  Command-line utilities
├── src/phishlens/            Reusable Python code
├── study/
│   ├── consent/              Consent and debriefing documents
│   ├── protocol/             Study protocol
│   └── questionnaires/       Participant instruments
└── tests/                    Automated tests
```

## Standard model output

Each model must return one JSON object containing:

- a verdict: `phishing`, `legitimate`, or `uncertain`
- confidence from 0 to 100
- observable evidence from the screenshot and supplied URL
- a short explanation for a non-expert user
- a safe recommended action
- a flag indicating whether human review is needed

The formal specification is in [`schemas/llm_output.schema.json`](schemas/llm_output.schema.json). The standard prompt is in [`prompts/phishing_analysis_v1.md`](prompts/phishing_analysis_v1.md).

## Validate a model response

This project currently uses only the Python standard library.

```bash
python3 scripts/validate_result.py examples/example_llm_output.json
```

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

## First cross-model test

Follow [`docs/first-model-test.md`](docs/first-model-test.md) after receiving an approved screenshot. Use the same screenshot, URL context, and prompt for every candidate model. Preserve the raw response before normalization.

## Research safeguards

- Do not visit live phishing pages for data collection or participant testing.
- Use static, verified screenshots from approved sources.
- Do not collect passwords, credentials, or unnecessary personal information.
- Obtain instructor and applicable IRB/HRPP guidance before recruiting participants.
- Keep participant identities separate from study responses.
- Treat LLM outputs as experimental observations, not security verdicts.
