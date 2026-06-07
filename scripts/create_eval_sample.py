from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.evaluation import evaluate_cases
from app.extraction import extract_case_documents
from app.reconciliation import reconcile_documents
from app.risk_scoring import score_case
from scripts.create_synthetic_cases import create_synthetic_cases


def load_documents(case_dir: Path) -> dict[str, str]:
    return {path.stem: path.read_text(encoding="utf-8") for path in sorted(case_dir.glob("*.txt"))}


def create_eval_sample(limit: int = 25):
    synthetic_dir = ROOT / "data" / "synthetic"
    cases = sorted(synthetic_dir.glob("LSI-*"))
    if len(cases) < limit:
        create_synthetic_cases(limit)
        cases = sorted(synthetic_dir.glob("LSI-*"))
    eval_dir = ROOT / "data" / "eval"
    pred_dir = ROOT / "output" / "eval_results"
    eval_dir.mkdir(parents=True, exist_ok=True)
    pred_dir.mkdir(parents=True, exist_ok=True)
    predictions = []
    truths = []
    detailed_predictions = []
    for case_dir in cases[:limit]:
        target = eval_dir / case_dir.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(case_dir, target)
        docs = load_documents(case_dir)
        extracted = extract_case_documents(docs, provider="mock")
        case = reconcile_documents(extracted)
        risk = score_case(case)
        truth = json.loads((case_dir / "ground_truth.json").read_text(encoding="utf-8"))
        truths.append(truth)
        predictions.append(case)
        detailed_predictions.append({"case_facts": case.model_dump(), "risk_score": risk.model_dump()})
    (pred_dir / "predictions.json").write_text(json.dumps(detailed_predictions, indent=2), encoding="utf-8")
    result = evaluate_cases(predictions, truths, output_dir=pred_dir)
    return result


if __name__ == "__main__":
    result = create_eval_sample()
    print(json.dumps(result.model_dump(), indent=2))
