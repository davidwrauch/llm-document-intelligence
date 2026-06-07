from pathlib import Path
from app.evaluation import evaluate_cases


def test_evaluation_metrics_expected_values(tmp_path: Path):
    truth = [{
        "case_id": "LSI-1",
        "worker_name": "Ana",
        "employer_name": "Cafe",
        "scheduled_hours": 48,
        "clocked_hours": 48,
        "paid_hours": 40,
        "hourly_rate": 20,
        "overtime_hours": 8,
        "total_paid": 800,
        "likely_violation": True,
        "violation_types": ["overtime", "underpayment"],
        "estimated_underpayment": 240,
    }]
    prediction = [{
        "case_id": "LSI-1",
        "worker_name": "Ana",
        "employer_name": "Cafe",
        "scheduled_hours": 48,
        "clocked_hours": 48,
        "paid_hours": 40,
        "hourly_rate": 20,
        "overtime_hours": 8,
        "total_paid": 800,
        "likely_violation": True,
        "violation_types": ["overtime", "underpayment"],
        "estimated_underpayment": 240,
    }]
    result = evaluate_cases(prediction, truth, output_dir=tmp_path)
    assert result.field_exact_match_accuracy == 1.0
    assert result.numeric_mae["estimated_underpayment"] == 0.0
    assert result.precision == 1.0
    assert result.recall == 1.0
    assert (tmp_path / "evaluation_summary.json").exists()
    assert (tmp_path / "evaluation_details.csv").exists()
