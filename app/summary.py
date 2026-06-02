from __future__ import annotations

from app.schemas import CaseFacts, InvestigatorSummary, RiskScore


def generate_summary(case: CaseFacts, risk: RiskScore) -> InvestigatorSummary:
    questions = [
        "Ask the employer for complete payroll registers and time records for the relevant week.",
        "Confirm whether meal breaks were actually taken and documented contemporaneously.",
        "Verify whether any overtime or spread-of-hours premiums were paid separately.",
    ]
    evidence_lines = []
    for dtype, facts in case.evidence_by_document.items():
        pieces = []
        for field in ["scheduled_hours", "clocked_hours", "paid_hours", "total_paid"]:
            value = getattr(facts, field)
            if value is not None:
                pieces.append(f"{field}={value}")
        evidence_lines.append(f"- **{dtype}**: " + (", ".join(pieces) if pieces else "supporting narrative only"))
    contradiction_lines = [f"- **{c.contradiction_type}** ({c.severity}): {c.description}" for c in case.contradictions]
    markdown = f"""# Investigator Summary: {case.case_id}

## Case overview
- Worker: {case.worker_name or 'Unknown'}
- Employer: {case.employer_name or 'Unknown'}
- Dates worked: {', '.join(case.dates_worked) if case.dates_worked else 'Unknown'}
- Scheduled / clocked / paid hours: {case.scheduled_hours} / {case.clocked_hours} / {case.paid_hours}
- Estimated underpayment: ${case.estimated_underpayment:.2f}

## Likely violations
{', '.join(case.violation_types) if case.violation_types else 'No likely violation detected'}

## Evidence by document
{chr(10).join(evidence_lines) if evidence_lines else '- No evidence loaded'}

## Contradictions
{chr(10).join(contradiction_lines) if contradiction_lines else '- No contradictions detected'}

## Risk score
- Score: {risk.risk_score}/100
- Severity: {risk.severity}
- Reasons: {'; '.join(risk.reasons)}

## Recommended follow-up questions
{chr(10).join(f'- {q}' for q in questions)}

## Human review flag
{risk.human_review_flag}
"""
    return InvestigatorSummary(
        case_id=case.case_id,
        markdown=markdown,
        human_review_flag=risk.human_review_flag,
        recommended_follow_up_questions=questions,
    )
