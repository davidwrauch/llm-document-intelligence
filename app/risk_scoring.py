from __future__ import annotations

from app.schemas import CaseFacts, RiskScore


def score_case(case: CaseFacts) -> RiskScore:
    score = 10
    reasons: list[str] = []
    if case.contradictions:
        points = min(45, len(case.contradictions) * 15)
        score += points
        reasons.append(f"{len(case.contradictions)} contradiction(s) detected (+{points}).")
    if case.estimated_underpayment > 0:
        points = min(25, int(case.estimated_underpayment / 25) + 10)
        score += points
        reasons.append(f"Estimated underpayment is ${case.estimated_underpayment:.2f} (+{points}).")
    if "overtime" in case.violation_types:
        score += 15
        reasons.append("Overtime issue present (+15).")
    if case.missing_fields:
        points = min(10, len(case.missing_fields) * 2)
        score += points
        reasons.append(f"Missing fields: {', '.join(case.missing_fields)} (+{points}).")
    if case.confidence < 0.65:
        score += 8
        reasons.append("Lower extraction confidence requires review (+8).")
    score = max(0, min(100, score))
    severity = "high" if score >= 70 else "medium" if score >= 40 else "low"
    if not reasons:
        reasons.append("No major contradictions or underpayment indicators found.")
    return RiskScore(risk_score=score, severity=severity, reasons=reasons, human_review_flag=score >= 40)
