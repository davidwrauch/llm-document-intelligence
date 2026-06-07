from app.reconciliation import reconcile_documents
from app.risk_scoring import score_case
from app.schemas import ExtractedDocumentFacts


def docs(paid_hours: float):
    return [
        ExtractedDocumentFacts(case_id="LSI-1", document_type="timekeeping", worker_name="Ana", employer_name="Cafe", clocked_hours=48, overtime_hours=8, hourly_rate=20),
        ExtractedDocumentFacts(case_id="LSI-1", document_type="payroll", worker_name="Ana", employer_name="Cafe", paid_hours=paid_hours, overtime_hours=8, overtime_paid=False, hourly_rate=20, total_paid=paid_hours * 20),
    ]


def test_detects_clocked_vs_paid_and_overtime_contradictions():
    case = reconcile_documents(docs(40))
    types = {c.contradiction_type for c in case.contradictions}
    assert "clocked_vs_paid_hours" in types
    assert "overtime_premium_missing" in types
    assert case.likely_violation is True


def test_risk_score_increases_with_contradictions():
    lower = score_case(reconcile_documents(docs(48))).risk_score
    higher = score_case(reconcile_documents(docs(40))).risk_score
    assert higher > lower
