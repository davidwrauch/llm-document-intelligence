from __future__ import annotations

import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.extraction import extract_case_documents
from app.reconciliation import reconcile_documents
from app.risk_scoring import score_case
from app.summary import generate_summary
from scripts.create_synthetic_cases import create_synthetic_cases


def load_case(case_dir: Path) -> dict[str, str]:
    return {path.stem: path.read_text(encoding="utf-8") for path in sorted(case_dir.glob("*.txt"))}


def run_demo_case(case_dir: Path | None = None):
    if case_dir is None:
        existing = sorted((ROOT / "data" / "synthetic").glob("LSI-*"))
        if not existing:
            existing = create_synthetic_cases(1)
        case_dir = existing[0]
    documents = load_case(case_dir)
    extracted = extract_case_documents(documents, provider="mock")
    case = reconcile_documents(extracted)
    risk = score_case(case)
    summary = generate_summary(case, risk)
    out_dir = ROOT / "output" / "demo_results"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "demo_case_summary.md").write_text(summary.markdown, encoding="utf-8")
    payload = {"case_facts": case.model_dump(), "risk_score": risk.model_dump(), "summary": summary.model_dump()}
    (out_dir / "demo_case_output.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_demo_case()
    print(result["summary"]["markdown"])
