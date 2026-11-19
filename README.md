# PhishLens

PhishLens examines how multimodal large language models classify visually
manipulated phishing websites and how model explanations affect human security
decisions. The project evaluates existing models rather than training a new
language model.

The repository uses static screenshots and structured model outputs. It
contains no live phishing workflow and collects no credentials.

## Study design

### Technical evaluation

ChatGPT, Claude, and Gemini receive the same static screenshot and versioned
prompt. The models do not receive a displayed URL and cannot browse the live
website. Each response records:

- a `phishing`, `legitimate`, or `uncertain` verdict
- confidence from 0 to 100
- the claimed brand
- visible supporting evidence
- a plain-language explanation
- a recommended action
- whether human review is appropriate

The reviewed study set contains 110 unique screenshots:

- 9 pilot screenshots
- 96 main screenshots
- 5 transfer screenshots

The set includes original legitimate and phishing pages together with
controlled visual variants covering 18 manipulation types. Each of the 110
screenshots is evaluated independently by all three models, producing 330
primary model evaluations.

### Human study

The human study compares three assistance conditions:

| Condition | Information shown |
|---|---|
| No assistance | Website screenshot only |
| Standard warning | Screenshot and a conventional security warning |
| LLM explanation | Screenshot, model verdict, confidence, explanation, and recommended action |

The study includes 100 eligible participants: 32 in the no-warning condition,
32 in the standard-warning condition, and 36 in the AI-explanation condition.
It measures classification accuracy, confidence, intended action, reliance on
correct and incorrect AI advice, and unaided transfer performance.

## Key results

### Technical evaluation

On the 42 original main-set screenshots, primary screenshot-only accuracy was:

| Model | Accuracy | Binary-decision coverage |
|---|---:|---:|
| Claude | 73.8% | 97.6% |
| ChatGPT | 14.3% | 14.3% |
| Gemini | 14.3% | 14.3% |

The low ChatGPT and Gemini accuracy values primarily reflect frequent
`uncertain` responses rather than frequent opposite-label decisions. Across the
54 controlled variants, ChatGPT returned 53 uncertain judgments, Gemini
returned 52, and Claude returned 28. Claude was most likely to flag flipping,
integration, and SRNet variants as phishing, while blur and rotation variants
were commonly judged legitimate. Manipulation-level results are descriptive
because each manipulation type contains three examples.

### Human study

| Condition | Main-task accuracy | Unaided transfer accuracy |
|---|---:|---:|
| No warning | 43.5% | 55.6% |
| Standard warning | 43.8% | 56.3% |
| AI explanation | 48.8% | 60.6% |

After accounting for screenshot-set differences, the AI-explanation condition
improved main-task accuracy by 5.8 percentage points over no warning, but the
difference was not statistically significant (`p = 0.135`). The corresponding
transfer improvement was 4.5 percentage points and was also not significant
(`p = 0.302`).

Participants followed 70.9% of correct AI recommendations and 87.5% of
incorrect AI recommendations. The higher reliance on incorrect advice was
statistically significant (`p = 0.0026`), providing evidence of automation
bias.

## Dataset organization

| File or folder | Contents |
|---|---|
| `data/manifest.csv` | Original legitimate and phishing sample metadata |
| `data/controlled_variants.csv` | Inventory of controlled visual variants |
| `data/experiment_subset.csv` | Pilot, main, and transfer experiment records |
| `review/pilot/` | Pilot screenshots and independent review decisions |
| `review/main/` | Main screenshots and independent review decisions |
| `review/transfer/` | Transfer screenshots and independent review decisions |

The primary repository dataset contains the 110 reviewed screenshots used in
the study. A separate expansion collection is retained locally and its image
files are intentionally excluded from version control.

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
      "category": "credential_request",
      "observation": "The page requests account credentials.",
      "risk_relevance": "Credential requests on an unverified page increase risk."
    }
  ],
  "explanation": "The page requests sensitive account information and should be verified independently.",
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
- Screenshot text is treated as untrusted webpage content.
- Model responses are experimental observations, not security guarantees.
- Review packages exclude personal and sensitive information.
- Additional expansion screenshots are kept locally and excluded from version
  control.
- Dataset and participant materials remain subject to their applicable sharing
  and consent restrictions.

## License

No open-source license is included. Repository contents remain protected by
default copyright.
