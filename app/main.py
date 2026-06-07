from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from app.extraction import extract_case_documents, extract_document_facts
from app.reconciliation import reconcile_documents
from app.risk_scoring import score_case
from app.schemas import CaseFacts, ExtractedDocumentFacts
from app.summary import generate_summary
from scripts.run_demo_case import run_demo_case

app = FastAPI(title="Labor Standards Investigation Intelligence System")


class ExtractRequest(BaseModel):
    document_text: str
    document_type: str
    provider: str = "mock"


class ReconcileRequest(BaseModel):
    documents: list[ExtractedDocumentFacts]


class ScoreRequest(BaseModel):
    case_facts: CaseFacts


class SummarizeRequest(BaseModel):
    case_facts: CaseFacts


class RunCaseRequest(BaseModel):
    documents: dict[str, str]
    provider: str = "mock"


@app.get("/")
def root():
    return {"name": "Labor Standards Investigation Intelligence System", "status": "ready"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/extract")
def extract(request: ExtractRequest):
    return extract_document_facts(request.document_text, request.document_type, provider=request.provider)


@app.post("/reconcile")
def reconcile(request: ReconcileRequest):
    return reconcile_documents(request.documents)


@app.post("/score")
def score(request: ScoreRequest):
    return score_case(request.case_facts)


@app.post("/summarize")
def summarize(request: SummarizeRequest):
    risk = score_case(request.case_facts)
    return generate_summary(request.case_facts, risk)


@app.post("/run-demo-case")
def run_demo(request: RunCaseRequest | None = None):
    if request and request.documents:
        extracted = extract_case_documents(request.documents, provider=request.provider)
        case = reconcile_documents(extracted)
        risk = score_case(case)
        summary = generate_summary(case, risk)
        return {"case_facts": case, "risk_score": risk, "summary": summary}
    return run_demo_case()
