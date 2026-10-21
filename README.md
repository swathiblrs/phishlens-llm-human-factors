# PhishLens

PhishLens examines how multimodal large language models classify visually
manipulated phishing websites and how model explanations affect human security
decisions. The project evaluates existing models rather than training a new
language model.

The repository uses static screenshots, simulated `.test` domains, and
structured model outputs. It contains no live phishing workflow and collects no
credentials.

## Study design

### Technical evaluation

ChatGPT, Claude, and Gemini receive the same screenshot, displayed URL, and
versioned prompt. Each response records:

- a `phishing`, `legitimate`, or `uncertain` verdict
- confidence from 0 to 100
- the claimed brand
- visible supporting evidence
- a plain-language explanation
- a recommended action
- whether human review is appropriate

The dataset includes original website screenshots, visible logo and layout
changes, and adversarial perturbations. The main experiment balances legitimate
and phishing URL contexts and covers the defined manipulation categories.

### Human study

The human study compares three assistance conditions:

| Condition | Information shown |
|---|---|
| No assistance | Website screenshot and displayed URL |
| Standard warning | Screenshot, URL, and a conventional warning |
| LLM explanation | Screenshot, URL, model verdict, and supporting evidence |

The study measures detection accuracy, decision time, confidence, trust,
reliance on incorrect advice, and later performance without AI assistance.

## Dataset organization

| File or folder | Contents |
|---|---|
| `data/manifest.csv` | Original legitimate and phishing sample metadata |
| `data/controlled_variants.csv` | Inventory of controlled visual variants |
| `data/experiment_subset.csv` | Pilot, main, and transfer experiment records |
| `review/pilot/` | Pilot screenshots and independent review decisions |
| `review/main/` | Main screenshots and independent review decisions |
| `review/transfer/` | Transfer screenshots and independent review decisions |

The experiment manifest defines one row per model input. A single reviewed
screenshot can appear in more than one experiment row when it is paired with
different URL contexts.

## Shared model prompt

The compact prompt is stored in
[`prompts/phishing_analysis_v1.md`](prompts/phishing_analysis_v1.md). The same
questions and JSON format apply to ChatGPT, Claude, and Gemini.

## Result organization

```text
results/
├── README.md
├── raw/
│   ├── chatgpt/
│   ├── claude/
│   └── gemini/
└── processed/
    ├── chatgpt_results.csv
    ├── claude_results.csv
    ├── gemini_results.csv
    └── sample_result.csv
```

The provider CSV files use the same 22-column format defined in
[`schemas/model_results_columns.csv`](schemas/model_results_columns.csv).
Complete unedited responses belong under the matching provider in
`results/raw/`. Normalized results belong in `results/processed/`.

## Standard model output

```json
{
  "sample_id": "sample-001",
  "verdict": "phishing",
  "confidence": 84,
  "claimed_brand": "Example Brand",
  "evidence": [
    {
      "category": "url_domain",
      "observation": "The displayed domain does not match the claimed brand.",
      "risk_relevance": "A brand-domain mismatch is a phishing indicator."
    }
  ],
  "explanation": "The claimed brand and displayed domain do not match.",
  "recommended_action": "verify_independently",
  "needs_human_review": true
}
```

The JSON specification is stored in
[`schemas/llm_output.schema.json`](schemas/llm_output.schema.json). The validator
is implemented in [`src/phishlens/validation.py`](src/phishlens/validation.py).

## Architecture

```text
Original screenshots and controlled variants
                    |
             Experiment subset
                    |
          Shared multimodal prompt
                    |
       +------------+------------+
       |            |            |
    ChatGPT       Claude       Gemini
       |            |            |
       +------------+------------+
                    |
        Raw and normalized results
                    |
       Technical and human analysis
```

## Repository structure

```text
phishlens-llm-human-factors/
├── analysis/                 Statistical analysis materials
├── data/
│   ├── controlled_variants.csv
│   ├── experiment_subset.csv
│   ├── manifest.csv
│   ├── original/
│   └── perturbed/
├── docs/                     Methodology and model-test documentation
├── examples/                 Example structured model output
├── paper/                    Proposal and report materials
├── presentation/             Presentation materials
├── prompts/                  Shared versioned model prompt
├── results/                  Provider-specific raw and processed results
├── review/                   Pilot, main, and transfer review packages
├── schemas/                  JSON schema and CSV column definitions
├── scripts/                  Dataset, review, and validation utilities
├── src/phishlens/            Reusable validation code
├── study/                    Human-study materials
└── tests/                    Automated validator tests
```

## Validation

Example response validation:

```bash
python3 scripts/validate_result.py examples/example_llm_output.json
```

Automated tests:

```bash
python3 -m unittest discover -s tests -v
```

## Safety and privacy

- Research inputs use static screenshots rather than live phishing pages.
- Reserved `.test` domains represent simulated phishing contexts.
- Screenshot text is treated as untrusted webpage content.
- Model responses are experimental observations, not security guarantees.
- Review packages exclude personal and sensitive information.
- Dataset and participant materials remain subject to their applicable sharing
  and consent restrictions.

## License

No open-source license is included. Repository contents remain protected by
default copyright.
