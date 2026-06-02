from __future__ import annotations

import json
import re
from typing import Any
from app.llm_client import LLMClient
from app.schemas import ExtractedDocumentFacts

VIOLATION_KEYWORDS = {
    "overtime": ["overtime", "premium", "time-and-a-half"],
    "unpaid_break": ["break", "meal"],
    "spread_of_hours": ["spread-of-hours", "spread of hours"],
    "underpayment": ["underpaid", "paid less", "missing pay"],
    "missing_premium": ["missing premium", "premium was not paid"],
}


def _number(patterns: list[str], text: str) -> float | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return float(match.group(1).replace(",", ""))
    return None


def _bool_from_text(text: str, positive: list[str], negative: list[str]) -> bool | None:
    lower = text.lower()
    if any(phrase in lower for phrase in negative):
        return False
    if any(phrase in lower for phrase in positive):
        return True
    return None


def rule_extract(document_text: str, document_type: str) -> dict[str, Any]:
    text = document_text
    case_id = re.search(r"Case ID:\s*([A-Z0-9_-]+)", text, re.I)
    worker = re.search(r"Worker:\s*([^\n]+)", text, re.I)
    employer = re.search(r"Employer:\s*([^\n]+)", text, re.I)
    dates = re.findall(r"\b(2026-\d{2}-\d{2})\b", text)
    lower = text.lower()
    violations = [name for name, keys in VIOLATION_KEYWORDS.items() if any(k in lower for k in keys)]

    return {
        "case_id": case_id.group(1) if case_id else "UNKNOWN",
        "document_type": document_type,
        "worker_name": worker.group(1).strip() if worker else None,
        "employer_name": employer.group(1).strip() if employer else None,
        "dates_worked": sorted(set(dates)),
        "scheduled_hours": _number([r"Scheduled hours:\s*([\d.]+)", r"scheduled\s+([\d.]+)\s+hours"], text),
        "clocked_hours": _number([r"Clocked hours:\s*([\d.]+)", r"clocked\s+([\d.]+)\s+hours"], text),
        "paid_hours": _number([r"Paid hours:\s*([\d.]+)", r"paid\s+for\s+([\d.]+)\s+hours"], text),
        "hourly_rate": _number([r"Hourly rate:\s*\$?([\d.]+)", r"\$([\d.]+)\s*/\s*hour"], text),
        "overtime_hours": _number([r"Overtime hours:\s*([\d.]+)", r"([\d.]+)\s+overtime hours"], text),
        "overtime_paid": _bool_from_text(text, ["overtime premium paid", "time-and-a-half paid"], ["no overtime premium", "overtime premium not paid", "no time-and-a-half"]),
        "total_paid": _number([r"Total paid:\s*\$?([\d,.]+)", r"paid total\s*\$?([\d,.]+)"], text),
        "break_deducted": _bool_from_text(text, ["break deducted", "meal break deducted"], ["no break deducted"]),
        "break_taken": _bool_from_text(text, ["break taken", "meal break taken"], ["no break taken", "was not able to take a break", "break was not taken"]),
        "spread_of_hours": _bool_from_text(text, ["spread-of-hours", "spread of hours"], ["no spread-of-hours"]),
        "premium_paid": _bool_from_text(text, ["premium paid"], ["premium not paid", "missing premium"]),
        "claimed_violation_types": violations,
        "raw_evidence": {"excerpt": text[:400]},
        "confidence": 0.86 if case_id else 0.55,
    }


def extract_document_facts(document_text: str, document_type: str, provider: str | None = None) -> ExtractedDocumentFacts:
    fallback = rule_extract(document_text, document_type)
    client = LLMClient(provider)
    if client.provider == "mock":
        return ExtractedDocumentFacts.model_validate(fallback)
    prompt = (
        "Extract labor investigation facts as JSON matching this schema keys: "
        f"{list(fallback.keys())}. Document type: {document_type}. Text:\n{document_text}"
    )
    data = {**fallback, **client.extract_json(prompt, fallback=fallback)}
    return ExtractedDocumentFacts.model_validate(data)


def extract_case_documents(documents: dict[str, str], provider: str | None = None) -> list[ExtractedDocumentFacts]:
    return [extract_document_facts(text, dtype, provider=provider) for dtype, text in documents.items()]
