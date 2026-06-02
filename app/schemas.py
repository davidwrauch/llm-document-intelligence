from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

DocumentType = Literal["worker_complaint", "schedule", "timekeeping", "payroll", "employer_message", "unknown"]
Severity = Literal["low", "medium", "high"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ExtractedDocumentFacts(StrictModel):
    case_id: str
    document_type: DocumentType
    worker_name: str | None = None
    employer_name: str | None = None
    dates_worked: list[str] = Field(default_factory=list)
    scheduled_hours: float | None = Field(default=None, ge=0)
    clocked_hours: float | None = Field(default=None, ge=0)
    paid_hours: float | None = Field(default=None, ge=0)
    hourly_rate: float | None = Field(default=None, ge=0)
    overtime_hours: float | None = Field(default=None, ge=0)
    overtime_paid: bool | None = None
    total_paid: float | None = Field(default=None, ge=0)
    break_deducted: bool | None = None
    break_taken: bool | None = None
    spread_of_hours: bool | None = None
    premium_paid: bool | None = None
    claimed_violation_types: list[str] = Field(default_factory=list)
    raw_evidence: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.75, ge=0, le=1)

    @field_validator("claimed_violation_types")
    @classmethod
    def normalize_violations(cls, values: list[str]) -> list[str]:
        return sorted({v.strip().lower().replace(" ", "_") for v in values if v.strip()})


class Contradiction(StrictModel):
    contradiction_type: str
    description: str
    documents: list[str]
    severity: Severity = "medium"
    confidence: float = Field(default=0.8, ge=0, le=1)


class CaseFacts(StrictModel):
    case_id: str
    worker_name: str | None = None
    employer_name: str | None = None
    dates_worked: list[str] = Field(default_factory=list)
    scheduled_hours: float | None = Field(default=None, ge=0)
    clocked_hours: float | None = Field(default=None, ge=0)
    paid_hours: float | None = Field(default=None, ge=0)
    hourly_rate: float | None = Field(default=None, ge=0)
    overtime_hours: float | None = Field(default=None, ge=0)
    overtime_paid: bool | None = None
    total_paid: float | None = Field(default=None, ge=0)
    likely_violation: bool = False
    violation_types: list[str] = Field(default_factory=list)
    estimated_underpayment: float = Field(default=0, ge=0)
    contradictions: list[Contradiction] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.7, ge=0, le=1)
    evidence_by_document: dict[str, ExtractedDocumentFacts] = Field(default_factory=dict)


class RiskScore(StrictModel):
    risk_score: int = Field(ge=0, le=100)
    severity: Severity
    reasons: list[str] = Field(default_factory=list)
    human_review_flag: bool = True


class InvestigatorSummary(StrictModel):
    case_id: str
    markdown: str
    human_review_flag: bool
    recommended_follow_up_questions: list[str] = Field(default_factory=list)


class EvaluationResult(StrictModel):
    field_exact_match_accuracy: float = Field(ge=0, le=1)
    numeric_mae: dict[str, float]
    violation_classification_accuracy: float = Field(ge=0, le=1)
    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    f1: float = Field(ge=0, le=1)
    case_count: int = Field(ge=0)
