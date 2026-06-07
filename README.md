# Labor Standards Investigation Intelligence System

A production-style Python demo for AI-assisted labor standards investigation workflows. Transforms unstructured workplace documents into structured facts, reconciles them across sources, scores for risk, and summarizes for human review.

## What it demonstrates

- LLM document extraction with deterministic mock fallback
- Structured JSON extraction using Pydantic schemas
- Multi-document reasoning and fact reconciliation
- Contradiction detection across complaints, schedules, time records, payroll, and employer messages
- Interpretable risk scoring (0–100)
- Human-in-the-loop investigator summaries
- Evaluation against known ground truth
- Production-style FastAPI endpoints

## Supported LLM providers

| Provider | Set in `.env` |
|---|---|
| Anthropic Claude | `LLM_PROVIDER=anthropic` |
| OpenAI | `LLM_PROVIDER=openai` |
| Mock (no key needed) | `LLM_PROVIDER=mock` |

If the selected provider's API key is missing, the client automatically falls back to mock mode.

## Project structure

```
.
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic/
│   └── eval/
├── scripts/
│   ├── download_datasets.py
│   ├── inspect_dataset.py
│   ├── create_synthetic_cases.py
│   ├── create_eval_sample.py
│   └── run_demo_case.py
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── llm_client.py
│   ├── extraction.py
│   ├── reconciliation.py
│   ├── risk_scoring.py
│   ├── evaluation.py
│   └── summary.py
├── tests/
└── output/
    ├── demo_results/
    └── eval_results/
```

## Setup

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### `.env` configuration

```env
LLM_PROVIDER=anthropic        # or openai, or mock
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=
DATABASE_URL=sqlite:///./data/processed/investigation_demo.db
```

> The project runs fully offline with `LLM_PROVIDER=mock` — no API key required.

## Usage

### Generate synthetic cases

```bash
python scripts/create_synthetic_cases.py
```

Creates 25+ cases under `data/synthetic/`. Each case includes:

- `worker_complaint.txt`
- `schedule.txt`
- `timekeeping.txt`
- `payroll.txt`
- `employer_message.txt`
- `ground_truth.json`

### Run the end-to-end demo

```bash
python scripts/run_demo_case.py
```

Runs extraction, reconciliation, contradiction detection, risk scoring, and summary on one case. Saves results to:

```
output/demo_results/demo_case_summary.md
output/demo_results/demo_case_output.json
```

### Run evaluation across all cases

```bash
python scripts/create_eval_sample.py
```

Compares predictions against ground truth. Saves to:

```
output/eval_results/predictions.json
output/eval_results/evaluation_summary.json
output/eval_results/evaluation_details.csv
```

Metrics include field-level exact match accuracy, numeric MAE, violation classification accuracy, precision, recall, and F1.

### Start the API server

```bash
uvicorn app.main:app --reload
```

Then open `http://localhost:8000/docs` for the interactive API explorer.

Available endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root |
| GET | `/health` | Health check |
| POST | `/extract` | Extract facts from a document |
| POST | `/reconcile` | Reconcile across documents |
| POST | `/score` | Score a case for risk |
| POST | `/summarize` | Generate investigator summary |
| POST | `/run-demo-case` | Run full pipeline |

### Run tests

```bash
pytest
```

### Download public benchmark datasets (optional)

```bash
python scripts/download_datasets.py
```

Attempts to fetch snapshots of:
- `theatticusproject/cuad` — legal/contract extraction
- `theatticusproject/cuad-qa` — QA-style extraction
- `nielsr/funsd` — form understanding
- `Voxel51/consolidated_receipt_dataset` — receipt extraction

Failures are skipped gracefully.

Inspect a dataset with:

```bash
python scripts/inspect_dataset.py theatticusproject/cuad
```

## Design notes

This demo favors readability over complexity. The mock extraction path uses transparent regex/rule-based extraction so the full workflow is reproducible locally without any API keys. The same schema and pipeline works with any supported LLM provider for richer extraction while preserving validation, reconciliation, risk scoring, summaries, and evaluation.

## Accuracy (Anthropic Claude, 25 synthetic cases)

Evaluated with `python scripts/create_eval_sample.py` against ground truth across 25 synthetic cases.

### Numeric field extraction

All numeric fields extracted with zero error:

| Field | MAE |
|---|---|
| Scheduled hours | 0.0 |
| Clocked hours | 0.0 |
| Paid hours | 0.0 |
| Hourly rate | 0.0 |
| Overtime hours | 0.0 |
| Total paid | 0.0 |
| Estimated underpayment | 0.0 |

### Violation classification

| Metric | Score |
|---|---|
| Exact match accuracy | 54.5% |
| Precision | 60.0% |
| Recall | 85.7% |
| F1 | 70.6% |

**Notes:**
- Numeric extraction is perfect because the synthetic documents contain clearly structured fields. Real-world documents will be harder.
- Violation classification recall (85.7%) is strong — the model catches most real violations. Precision (60%) is lower, meaning it sometimes flags violations that aren't in the ground truth. For an investigative tool, high recall is the right trade-off: it's better to over-flag than to miss a genuine violation.
- Exact match accuracy (54.5%) is lower because it requires the predicted violation set to match ground truth exactly — any extra or missing label counts as a miss.
