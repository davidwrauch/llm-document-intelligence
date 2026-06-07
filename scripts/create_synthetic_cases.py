from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "synthetic"

NAMES = ["Ana Rivera", "Malik Johnson", "Priya Shah", "Diego Torres", "Mei Chen", "Sam Patel", "Rosa Kim", "Jordan Lee"]
EMPLOYERS = ["Bright Deli LLC", "Metro Cleaners", "Northstar Bistro", "Harbor Grocery", "Summit Home Care"]
VIOLATION_PATTERNS = ["overtime", "unpaid_break", "spread_of_hours", "missing_premium", "employer_conflict"]


def case_values(i: int) -> dict:
    pattern = VIOLATION_PATTERNS[i % len(VIOLATION_PATTERNS)]
    scheduled = 42 + (i % 4) * 2
    clocked = scheduled + (2 if pattern in {"overtime", "unpaid_break"} else 0)
    paid = 40 if pattern in {"overtime", "employer_conflict"} else max(38, clocked - 2)
    rate = 15 + (i % 6)
    overtime = max(clocked - 40, 0)
    expected = min(clocked, 40) * rate + overtime * rate * 1.5
    if pattern == "missing_premium":
        total_paid = round(clocked * rate, 2)
    else:
        total_paid = round(paid * rate, 2)
    underpayment = round(max(expected - total_paid, 0), 2)
    dates = [f"2026-05-{day:02d}" for day in range(4 + (i % 10), 9 + (i % 10))]
    violations = sorted({pattern, "underpayment", *( ["overtime"] if overtime > 0 else [] )})
    return {
        "case_id": f"LSI-{i:04d}",
        "worker_name": NAMES[i % len(NAMES)],
        "employer_name": EMPLOYERS[i % len(EMPLOYERS)],
        "dates_worked": dates,
        "scheduled_hours": float(scheduled),
        "clocked_hours": float(clocked),
        "paid_hours": float(paid),
        "hourly_rate": float(rate),
        "overtime_hours": float(overtime),
        "total_paid": total_paid,
        "likely_violation": True,
        "violation_types": violations,
        "estimated_underpayment": underpayment,
        "contradiction_expected": True,
        "pattern": pattern,
    }


def write_case(case: dict) -> None:
    case_dir = DATA_DIR / case["case_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    dates = ", ".join(case["dates_worked"])
    no_break = case["pattern"] == "unpaid_break"
    premium_conflict = case["pattern"] in {"missing_premium", "employer_conflict"}
    docs = {
        "worker_complaint.txt": f"""Case ID: {case['case_id']}
Worker: {case['worker_name']}
Employer: {case['employer_name']}
Dates worked: {dates}
I clocked {case['clocked_hours']} hours at ${case['hourly_rate']}/hour. I was paid for {case['paid_hours']} hours and believe I was underpaid. {'I was not able to take a break and no break taken.' if no_break else 'Meal break taken on most days.'} Overtime premium not paid.
""",
        "schedule.txt": f"""Case ID: {case['case_id']}
Worker: {case['worker_name']}
Employer: {case['employer_name']}
Dates: {dates}
Scheduled hours: {case['scheduled_hours']}
Shift notes: spread-of-hours issue {'observed' if case['pattern'] == 'spread_of_hours' else 'not central'}.
""",
        "timekeeping.txt": f"""Case ID: {case['case_id']}
Worker: {case['worker_name']}
Employer: {case['employer_name']}
Dates worked: {dates}
Clocked hours: {case['clocked_hours']}
Overtime hours: {case['overtime_hours']}
Break deducted: {'yes' if no_break else 'no'}
""",
        "payroll.txt": f"""Case ID: {case['case_id']}
Worker: {case['worker_name']}
Employer: {case['employer_name']}
Paid hours: {case['paid_hours']}
Hourly rate: ${case['hourly_rate']}
Overtime hours: {case['overtime_hours']}
No overtime premium.
Total paid: ${case['total_paid']}
Meal break deducted: {'yes' if no_break else 'no'}
Premium paid: {'yes' if premium_conflict else 'no'}
""",
        "employer_message.txt": f"""Case ID: {case['case_id']}
Worker: {case['worker_name']}
Employer: {case['employer_name']}
Manager message: Payroll only approved 40 regular hours. {'Premium not paid due to system issue.' if premium_conflict else 'No separate premium was authorized.'} Please keep schedule changes informal.
""",
    }
    for filename, text in docs.items():
        (case_dir / filename).write_text(text.strip() + "\n", encoding="utf-8")
    truth = {k: v for k, v in case.items() if k != "pattern"}
    (case_dir / "ground_truth.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")


def create_synthetic_cases(count: int = 25) -> list[Path]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for i in range(1, count + 1):
        case = case_values(i)
        write_case(case)
        paths.append(DATA_DIR / case["case_id"])
    return paths


if __name__ == "__main__":
    paths = create_synthetic_cases()
    print(f"Created {len(paths)} synthetic cases in {DATA_DIR}")
