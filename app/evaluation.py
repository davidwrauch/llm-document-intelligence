from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from app.schemas import CaseFacts, EvaluationResult

EXACT_FIELDS = ["case_id", "worker_name", "employer_name", "likely_violation"]
NUMERIC_FIELDS = ["scheduled_hours", "clocked_hours", "paid_hours", "hourly_rate", "overtime_hours", "total_paid", "estimated_underpayment"]


def _as_dict(prediction: CaseFacts | dict[str, Any]) -> dict[str, Any]:
    return prediction.model_dump() if isinstance(prediction, CaseFacts) else prediction


def evaluate_cases(predictions: list[CaseFacts | dict[str, Any]], ground_truths: list[dict[str, Any]], output_dir: str | Path = "output/eval_results") -> EvaluationResult:
    rows = []
    exact_hits = 0
    exact_total = 0
    mae_values = {field: [] for field in NUMERIC_FIELDS}
    true_labels = []
    pred_labels = []

    for pred_obj, truth in zip(predictions, ground_truths):
        pred = _as_dict(pred_obj)
        row = {"case_id": truth.get("case_id", pred.get("case_id"))}
        for field in EXACT_FIELDS:
            hit = pred.get(field) == truth.get(field)
            exact_hits += int(hit)
            exact_total += 1
            row[f"{field}_exact"] = hit
        for field in NUMERIC_FIELDS:
            p = pred.get(field)
            t = truth.get(field)
            if p is not None and t is not None:
                err = abs(float(p) - float(t))
                mae_values[field].append(err)
                row[f"{field}_abs_error"] = err
        truth_set = set(truth.get("violation_types", []))
        pred_set = set(pred.get("violation_types", []))
        for label in sorted(truth_set | pred_set | {"none"}):
            if label == "none" and (truth_set or pred_set):
                continue
            true_labels.append(1 if label in truth_set else 0)
            pred_labels.append(1 if label in pred_set else 0)
        row["truth_violations"] = ";".join(sorted(truth_set))
        row["pred_violations"] = ";".join(sorted(pred_set))
        rows.append(row)

    precision, recall, f1, _ = precision_recall_fscore_support(true_labels, pred_labels, average="binary", zero_division=0)
    violation_accuracy = accuracy_score(true_labels, pred_labels) if true_labels else 1.0
    result = EvaluationResult(
        field_exact_match_accuracy=exact_hits / exact_total if exact_total else 1.0,
        numeric_mae={field: (sum(vals) / len(vals) if vals else 0.0) for field, vals in mae_values.items()},
        violation_classification_accuracy=violation_accuracy,
        precision=float(precision),
        recall=float(recall),
        f1=float(f1),
        case_count=len(rows),
    )
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "evaluation_summary.json").write_text(json.dumps(result.model_dump(), indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(output / "evaluation_details.csv", index=False)
    return result
