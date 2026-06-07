import pytest
from pydantic import ValidationError
from app.schemas import ExtractedDocumentFacts


def test_extracted_document_accepts_valid_fact():
    fact = ExtractedDocumentFacts(
        case_id="LSI-TEST",
        document_type="payroll",
        paid_hours=40,
        hourly_rate=18,
        total_paid=720,
        confidence=0.9,
    )
    assert fact.case_id == "LSI-TEST"
    assert fact.claimed_violation_types == []


def test_extracted_document_rejects_negative_hours():
    with pytest.raises(ValidationError):
        ExtractedDocumentFacts(case_id="LSI-TEST", document_type="payroll", paid_hours=-1)
