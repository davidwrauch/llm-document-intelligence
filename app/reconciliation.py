from __future__ import annotations

from statistics import mean
from app.schemas import CaseFacts, Contradiction, ExtractedDocumentFacts

FIELDS = ["worker_name", "employer_name", "scheduled_hours", "clocked_hours", "paid_hours", "hourly_rate", "overtime_hours", "total_paid"]


def _first_value(docs: list[ExtractedDocumentFacts], field: str):
    for doc in docs:
        value = getattr(doc, field)
        if value not in (None, [], ""):
            return value
    return None


def reconcile_documents(docs: list[ExtractedDocumentFacts]) -> CaseFacts:
    if not docs:
        raise ValueError("At least one extracted document is required")
    by_type = {doc.document_type: doc for doc in docs}
    case_id = _first_value(docs, "case_id") or "UNKNOWN"
    values = {field: _first_value(docs, field) for field in FIELDS}
    dates = sorted({date for doc in docs for date in doc.dates_worked})
    violations = sorted({v for doc in docs for v in doc.claimed_violation_types})
    contradictions: list[Contradiction] = []

    scheduled = values["scheduled_hours"]
    clocked = values["clocked_hours"]
    paid = values["paid_hours"]
    overtime = values["overtime_hours"] or max((clocked or 0) - 40, 0)
    rate = values["hourly_rate"] or 0
    total_paid = values["total_paid"]

    if clocked is not None and paid is not None and clocked > paid + 0.01:
        contradictions.append(Contradiction(
            contradiction_type="clocked_vs_paid_hours",
            description=f"Timekeeping shows {clocked} hours but payroll shows {paid} paid hours.",
            documents=["timekeeping", "payroll"],
            severity="high",
        ))
        violations.append("underpayment")

    if scheduled is not None and paid is not None and scheduled > paid + 0.01:
        contradictions.append(Contradiction(
            contradiction_type="scheduled_vs_paid_hours",
            description=f"Schedule shows {scheduled} hours but payroll shows {paid} paid hours.",
            documents=["schedule", "payroll"],
            severity="medium",
        ))

    payroll = by_type.get("payroll")
    if overtime > 0 and payroll and payroll.overtime_paid is False:
        contradictions.append(Contradiction(
            contradiction_type="overtime_premium_missing",
            description=f"The case has {overtime} overtime hours and payroll indicates no overtime premium.",
            documents=["timekeeping", "payroll"],
            severity="high",
        ))
        violations.append("overtime")

    complaint = by_type.get("worker_complaint")
    if complaint and payroll and complaint.break_taken is False and payroll.break_deducted is True:
        contradictions.append(Contradiction(
            contradiction_type="break_deduction_disputed",
            description="Worker says no break was taken, while payroll deducted break time.",
            documents=["worker_complaint", "payroll"],
            severity="medium",
        ))
        violations.append("unpaid_break")

    employer = by_type.get("employer_message")
    if employer and payroll and employer.premium_paid is False and payroll.premium_paid is True:
        contradictions.append(Contradiction(
            contradiction_type="premium_record_conflict",
            description="Employer message says a premium was not paid, while payroll marks premium paid.",
            documents=["employer_message", "payroll"],
            severity="medium",
        ))

    expected_regular = min(clocked or paid or 0, 40) * rate
    expected_ot = max(overtime or 0, 0) * rate * 1.5
    expected_total = expected_regular + expected_ot
    estimated_underpayment = max(round(expected_total - (total_paid or 0), 2), 0)
    if estimated_underpayment > 0:
        violations.append("underpayment")

    missing = [field for field, value in values.items() if value in (None, [], "")]
    confidence = max(0.35, min(0.95, mean(doc.confidence for doc in docs) - 0.03 * len(missing)))
    return CaseFacts(
        case_id=case_id,
        worker_name=values["worker_name"],
        employer_name=values["employer_name"],
        dates_worked=dates,
        scheduled_hours=scheduled,
        clocked_hours=clocked,
        paid_hours=paid,
        hourly_rate=rate or None,
        overtime_hours=overtime,
        overtime_paid=payroll.overtime_paid if payroll else None,
        total_paid=total_paid,
        likely_violation=bool(contradictions or estimated_underpayment > 0),
        violation_types=sorted(set(violations)),
        estimated_underpayment=estimated_underpayment,
        contradictions=contradictions,
        missing_fields=missing,
        confidence=round(confidence, 3),
        evidence_by_document={doc.document_type: doc for doc in docs},
    )
