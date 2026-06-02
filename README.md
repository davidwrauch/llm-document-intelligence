# Labor Standards Investigation Intelligence System

A production-style Python demo for AI-assisted labor standards investigation workflows. It shows how unstructured workplace documents can be transformed into structured facts, reconciled across documents, scored for risk, summarized for human review, and evaluated against ground truth.

This project uses **synthetic labor-enforcement documents** for the domain demo, so it does not require real confidential enforcement records. It also includes scripts that attempt to download public benchmark datasets for broader extraction experiments.

## What it demonstrates

- LLM-style document extraction with deterministic mock mode
- Structured JSON extraction using Pydantic schemas
- Multi-document reasoning and fact reconciliation
- Contradiction detection across complaints, schedules, time records, payroll, and employer messages
- Interpretable risk scoring from 0-100
- Human-in-the-loop investigator summaries
- Evaluation against known ground truth
- Production-style FastAPI endpoints

## Supported public benchmark datasets

The dataset downloader attempts to fetch and save snapshots of:

- `theatticusproject/cuad` for legal/contract extraction and clause detection evaluation
- `theatticusproject/cuad-qa` for question-answer style extraction if useful
- `nielsr/funsd` for form understanding / structured extraction evaluation
- `Voxel51/consolidated_receipt_dataset` for receipt extraction if easy to load

Dataset loading is intentionally graceful: if a dataset is unavailable, gated, slow, or incompatible in the local environment, the script prints the failure and continues.

## Project structure

```text
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

## Setup on Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

The default `.env.example` values are:

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LLM_PROVIDER=mock
DATABASE_URL=sqlite:///./data/processed/investigation_demo.db
```

The project works without paid API keys because `LLM_PROVIDER=mock` uses deterministic rule-based extraction for the synthetic documents.

## Run synthetic data generation

```powershell
python scripts/create_synthetic_cases.py
```

This creates at least 25 cases under `data/synthetic`. Each case includes:

- `worker_complaint.txt`
- `schedule.txt`
- `timekeeping.txt`
- `payroll.txt`
- `employer_message.txt`
- `ground_truth.json`

The cases include realistic contradictions such as scheduled hours exceeding paid hours, clocked overtime without overtime premium, disputed unpaid breaks, spread-of-hours issues, missing premiums, and employer messages that conflict with payroll records.

## Run the end-to-end demo

```powershell
python scripts/run_demo_case.py
```

The demo performs extraction, reconciliation, contradiction detection, risk scoring, and summary generation. It saves:

- `output/demo_results/demo_case_summary.md`
- `output/demo_results/demo_case_output.json`

## Run evaluation

```powershell
python scripts/create_eval_sample.py
```

This runs the pipeline across synthetic cases, compares predictions with ground truth, and saves:

- `output/eval_results/predictions.json`
- `output/eval_results/evaluation_summary.json`
- `output/eval_results/evaluation_details.csv`

Metrics include field-level exact match accuracy, numeric mean absolute error, violation classification accuracy, precision, recall, and F1.

## Download public datasets

```powershell
python scripts/download_datasets.py
```

Downloaded snapshots are saved under `data/raw` when possible. Failures are skipped gracefully with clear messages.

Inspect a dataset with:

```powershell
python scripts/inspect_dataset.py theatticusproject/cuad
```

## Run the API

```powershell
uvicorn app.main:app --reload
```

Endpoints:

- `GET /`
- `GET /health`
- `POST /extract`
- `POST /reconcile`
- `POST /score`
- `POST /summarize`
- `POST /run-demo-case`

The API accepts text payloads and structured JSON payloads; it does not require a frontend.

## Run tests

```powershell
pytest
```

## Optional real LLM providers

Set `LLM_PROVIDER=openai` and `OPENAI_API_KEY` to use OpenAI, or set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` to use Anthropic. If the selected API key is missing, the client automatically falls back to mock mode.

## Design notes

This demo intentionally favors readability over complexity. The mock extraction path uses transparent regex/rule extraction so the entire workflow is reproducible locally. The same schema and pipeline can be used with an LLM provider for richer extraction prompts while preserving validation, reconciliation, risk scoring, summaries, and evaluation.
