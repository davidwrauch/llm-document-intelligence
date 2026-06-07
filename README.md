# Labor Standards Investigation Intelligence System

A working demonstration of AI-powered document intelligence applied to labor standards investigations — transforming messy, fragmented workplace documents into structured, decision-grade intelligence.

---

## What this is

Insurance and regulatory workflows are drowning in unstructured documents. This system shows what it looks like when an LLM pipeline actually processes them: ingesting worker complaints, schedules, timekeeping records, payroll data, and employer messages, then surfacing contradictions, flagging violations, and scoring risk — all in a format a human investigator can act on immediately.

This is the same core capability that powers Tailshift's underwriting intelligence: take the mess of real-world documents, find the signal, and deliver it fast.

---

## What it does

Given a set of workplace documents for a single case, the system:

1. **Extracts structured facts** from each document (hours worked, pay rates, schedules, employer claims) using Claude or OpenAI
2. **Reconciles facts across documents** — finding where the worker's complaint, the schedule, timekeeping, and payroll records agree or conflict
3. **Detects contradictions** and classifies their severity (e.g., timekeeping shows 46 hours worked, payroll shows 40 hours paid)
4. **Scores risk** on a 0–100 scale with interpretable reasoning
5. **Generates an investigator summary** — a concise, human-readable brief with follow-up recommendations

### Sample output (one real case run)

```
Worker: Malik Johnson | Employer: Metro Cleaners
Scheduled / clocked / paid hours: 44.0 / 46.0 / 40.0
Estimated underpayment: $80.00
Risk score: 83/100 (high)

Key contradictions:
  - Timekeeping shows 46h worked, payroll shows 40h paid [HIGH]
  - No overtime premium despite 6h overtime [HIGH]
  - Worker disputes break deduction not reflected in payroll [MEDIUM]

Violations flagged: overtime, underpayment, break denial, unauthorized schedule changes
Recommended: Request full payroll register; confirm break documentation; verify OT premium payments
```

---

## Accuracy (Claude, 25 synthetic cases)

| What we measured | Result |
|---|---|
| Numeric field extraction (hours, pay rates, totals) | **Perfect — 0.0 MAE across all fields** |
| Violation detection recall | **85.7%** — catches most real violations |
| Violation detection precision | 60.0% — some over-flagging (acceptable for investigative use) |
| Exact match accuracy | 54.5% |

For investigative tools, high recall is the right trade-off: it's better to surface a potential violation for human review than to miss a genuine one. The system is designed to support — not replace — investigator judgment.

---

## Running it

### Setup (Mac / Linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your API key
```

### Setup (Windows)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### `.env` configuration

```env
LLM_PROVIDER=anthropic        # or openai, or mock
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=
DATABASE_URL=sqlite:///./data/processed/investigation_demo.db
```

No API key? Set `LLM_PROVIDER=mock` — the full pipeline runs offline using rule-based extraction.

---

## Key commands

| What you want to do | Command |
|---|---|
| Run the end-to-end demo on one case | `python scripts/run_demo_case.py` |
| Evaluate across all 25 synthetic cases | `python scripts/create_eval_sample.py` |
| Start the REST API | `uvicorn app.main:app --reload` |
| Generate more synthetic cases | `python scripts/create_synthetic_cases.py` |
| Run tests | `pytest` |

Demo output lands in `output/demo_results/`. Evaluation results (metrics, per-case predictions) land in `output/eval_results/`.

---

## API endpoints

Start the server (`uvicorn app.main:app --reload`), then visit `http://localhost:8000/docs` for the interactive explorer.

| Endpoint | What it does |
|---|---|
| `POST /extract` | Extract structured facts from one document |
| `POST /reconcile` | Reconcile facts across multiple documents |
| `POST /score` | Score a case for risk |
| `POST /summarize` | Generate investigator summary |
| `POST /run-demo-case` | Run the full pipeline end to end |

---

## LLM providers

| Provider | `.env` setting |
|---|---|
| Anthropic Claude | `LLM_PROVIDER=anthropic` |
| OpenAI | `LLM_PROVIDER=openai` |
| Mock (no key needed) | `LLM_PROVIDER=mock` |

The client falls back to mock automatically if a provider's key is missing.

---

## Project structure

```
.
├── app/                    Core pipeline modules
│   ├── extraction.py       LLM-powered document extraction
│   ├── reconciliation.py   Cross-document fact reconciliation
│   ├── risk_scoring.py     Interpretable 0–100 risk scoring
│   ├── evaluation.py       Ground truth comparison
│   ├── summary.py          Investigator summary generation
│   ├── schemas.py          Pydantic data models
│   ├── llm_client.py       Provider-agnostic LLM client
│   ├── main.py             FastAPI app
│   ├── config.py           Environment configuration
│   └── database.py         SQLite persistence
├── data/
│   ├── synthetic/          25 generated cases with ground truth
│   ├── eval/               Held-out evaluation cases
│   ├── raw/                Source data (gitignored)
│   └── processed/          Pipeline outputs (gitignored)
├── scripts/                CLI entry points
├── tests/                  Unit tests
└── output/
    ├── demo_results/       Latest demo run output
    └── eval_results/       Latest evaluation run output
```

---

## Design philosophy

The pipeline is transparent by design. The mock extraction path uses readable regex/rule-based logic so the full workflow is reproducible without any API keys. The same schemas, reconciliation logic, risk scoring, and evaluation framework run identically whether the extraction comes from Claude, GPT-4, or mock mode — making it easy to swap providers or benchmark them head to head.
