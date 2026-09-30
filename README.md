# PhishLens

**When an AI confidently misreads a phishing page, will people trust it anyway?**

PhishLens studies how multimodal large language models (MLLMs) detect visually manipulated phishing websites and how their explanations influence human decisions. We test existing multimodal models on original and modified website screenshots, record when their verdicts and explanations fail, and use selected outputs in a controlled user study.

We are not building or training a new LLM. We are evaluating models such as GPT, Claude, and Gemini under the same experimental conditions.

Static screenshots only. No live phishing websites. No credential collection.

## Why this exists

Phishing websites imitate trusted services to steal passwords and other sensitive information. Visual phishing detectors and MLLMs can inspect webpage screenshots for suspicious branding, login forms, layouts, and mismatches between a claimed brand and a displayed URL.

However, attackers can alter logos, colors, layouts, and brand-related cues while keeping a page convincing. These changes may cause a model to produce an incorrect verdict. Because an MLLM can also generate a fluent and confident explanation, its error may persuade a user to trust a phishing page.

Existing work has evaluated visual phishing detectors, multimodal phishing detection, and explainable warnings. PhishLens connects these areas by examining both model robustness and what happens when people receive correct or incorrect AI-generated security advice.

## How it works

1. **Prepare the dataset.** Collect verified legitimate and phishing website screenshots from approved research datasets.
2. **Create controlled variants.** Modify one visual category at a time, including logos, colors/layouts, and visible brand or URL cues.
3. **Evaluate the models.** Give GPT, Claude, and Gemini the same screenshot, displayed URL, and versioned prompt.
4. **Record the results.** Preserve each model's verdict, confidence, cited evidence, explanation, recommended action, latency, and raw response.
5. **Review explanation quality.** Check whether the evidence is visible, factually supported, understandable, and connected to a safe recommendation.
6. **Select study examples.** Choose correct and incorrect MLLM outputs from the technical evaluation.
7. **Run the user study.** Compare participant decisions with no warning, a conventional warning, and an MLLM evidence-based explanation.
8. **Measure the outcome.** Analyze detection accuracy, decision time, confidence, trust, over-reliance on incorrect advice, and later unaided performance.

## Features

- Two-stage evaluation connecting model failures with human security decisions
- Controlled original-versus-modified screenshot comparisons
- Support for GPT, Claude, and Gemini candidate models
- Versioned prompt shared across all model runs
- Structured JSON output for verdicts, evidence, explanations, and recommendations
- Raw-response preservation and CSV normalization
- Explanation-quality coding for factual support, clarity, and safety
- Planned three-condition human study
- Planned transfer test without AI assistance
- Reproducible dataset manifest, validation scripts, and analysis materials

## Experimental design

### Stage 1: MLLM robustness evaluation

The proposed evaluation will use legitimate, original phishing, and visually manipulated phishing screenshots. Each model will receive the same input and will classify the sample as `phishing`, `legitimate`, or `uncertain`.

The planned visual manipulation categories are:

| Category | Examples |
|---|---|
| Logo modification | Removal, replacement, scaling, rotation, blurring, or adversarial perturbation |
| Color and layout | Color replacement, repositioning, or layout modification |
| Brand and URL cues | Brand-text changes, font/case changes, or mismatched displayed domains |

The project currently includes Professor Kim's perturbation dataset with Swin, ViT, CW, FGM, PGD, and SRNet examples. These samples will be paired with verified labels and URL context before formal evaluation.

### Stage 2: Human study

Subject to instructor and IRB/HRPP approval, adult participants will classify randomized website screenshots under one of three conditions:

| Condition | Participant sees |
|---|---|
| No warning | Website screenshot and displayed URL only |
| Conventional warning | Screenshot, URL, and a standard phishing warning |
| MLLM explanation | Screenshot, URL, model verdict, and evidence-based explanation |

The MLLM condition will include both correct and incorrect recommendations observed during Stage 1. A final unaided task is planned to measure whether participants can apply what they learned without AI assistance.

## Standard model output

Each model response is normalized into one JSON object:

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
      "risk_relevance": "A brand-domain mismatch is a common phishing indicator."
    }
  ],
  "explanation": "The claimed brand and displayed domain do not match. Verify the site independently before entering information.",
  "recommended_action": "verify_independently",
  "needs_human_review": true
}
```

The complete schema is in [`schemas/llm_output.schema.json`](schemas/llm_output.schema.json), and the standard prompt is in [`prompts/phishing_analysis_v1.md`](prompts/phishing_analysis_v1.md).

## Safety and privacy

A project involving phishing material and human participants requires strict safeguards:

- **Static screenshots only.** The study does not require participants or researchers to open live phishing pages.
- **No credentials.** PhishLens does not request, collect, or store passwords or authentication data.
- **Untrusted screenshot text.** The prompt tells models to treat visible webpage text as content, not instructions.
- **Verified labels.** Two team members will independently review screenshot labels and controlled modifications.
- **Human review.** Model responses are experimental observations, not authoritative security verdicts.
- **Participant privacy.** Planned study responses will use randomized participant identifiers.
- **Separate contact data.** Compensation contact information, if used, will be stored separately from study responses.
- **Approval before recruitment.** No participant recruitment will begin before the required instructor and IRB/HRPP guidance.
- **License-aware sharing.** Dataset images and participant data will be shared only when their licenses and consent terms permit it.

## Architecture

| Layer | Purpose | Current implementation |
|---|---|---|
| Dataset layer | Stores approved originals, controlled variants, labels, provenance, and manipulation metadata | `data/` and `data/manifest.csv` |
| Prompt layer | Gives every MLLM the same instructions and input structure | `prompts/phishing_analysis_v1.md` |
| Model layer | Runs the same screenshot and URL context through GPT, Claude, and Gemini | Manual interfaces initially; APIs if available |
| Response layer | Preserves raw responses and normalizes structured fields | `results/raw/`, `results/processed/`, and `schemas/` |
| Validation layer | Checks verdicts, confidence ranges, evidence fields, and output structure | `src/phishlens/validation.py` and `scripts/validate_result.py` |
| Analysis layer | Will calculate model performance, confidence calibration, explanation quality, and human-study outcomes | Planned under `analysis/` |
| Study layer | Will contain consent, protocol, questionnaires, warning conditions, and debriefing materials | Planned under `study/` |

```text
Approved screenshots
        │
        ├── Original samples
        └── Controlled visual variants
                    │
                    ▼
          Versioned MLLM prompt
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
         GPT      Claude    Gemini
          └─────────┼─────────┘
                    ▼
       Raw responses and validated JSON
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
  Technical evaluation   Human-study stimuli
                              │
                              ▼
                 Accuracy, trust, reliance,
                    and transfer analysis
```

## Getting started

### Prerequisites

- Python 3.10 or newer
- Git
- An approved static screenshot for model testing
- Access to the candidate multimodal model interfaces or APIs

The current validation tools use only the Python standard library.

### 1. Clone the repository

```bash
git clone https://github.com/swathiblrs/phishlens-llm-human-factors.git
cd phishlens-llm-human-factors
```

### 2. Validate the example response

```bash
python3 scripts/validate_result.py examples/example_llm_output.json
```

### 3. Run the tests

```bash
python3 -m unittest discover -s tests -v
```

### 4. Test a screenshot

Follow [`docs/first-model-test.md`](docs/first-model-test.md) after receiving and verifying an approved static screenshot. Use the exact same screenshot, displayed URL, and prompt for every model. Do not include the ground-truth label or modification type in the prompt.

If a model does not return valid JSON, preserve the raw response and record a formatting failure. Do not rerun a response only because its result is undesirable.

## Project layout

```text
phishlens-llm-human-factors/
├── analysis/                 Planned statistical analysis code
├── data/
│   ├── original/             Approved original screenshots
│   ├── perturbed/            Controlled visual variants
│   └── manifest.csv          Labels, provenance, and manipulation metadata
├── docs/                     Methodology and testing instructions
├── examples/                 Example structured model output
├── paper/                    Proposal and report materials
├── presentation/             Presentation materials
├── prompts/                  Versioned MLLM prompts
├── results/
│   ├── raw/                  Complete provider responses
│   └── processed/            Validated and normalized results
├── schemas/                  JSON and CSV specifications
├── scripts/                  Command-line utilities
├── src/phishlens/            Reusable Python code
├── study/
│   ├── consent/              Planned consent and debriefing materials
│   ├── protocol/             Planned human-study protocol
│   └── questionnaires/       Planned participant instruments
└── tests/                    Automated validator tests
```

## Testing

The unit tests verify valid responses and reject unsupported verdicts, out-of-range confidence values, and unexpected fields:

```bash
python3 -m unittest discover -s tests -v
```

To validate a specific normalized response:

```bash
python3 scripts/validate_result.py path/to/result.json
```

## License

No open-source license has been selected yet. Until a license is added, the repository contents remain protected by default copyright and should not be reused without permission.
