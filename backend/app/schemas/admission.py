from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AdmissionImportResponse(BaseModel):
    doc_id: str
    title: str
    pages: int
    chunks: int


class AdmissionQueryRequest(BaseModel):
    question: str
    language: Optional[str] = "vi"
    session_id: Optional[str] = None
    top_k: int = Field(default=6, ge=1, le=12)


class AdmissionCitation(BaseModel):
    doc_id: str
    title: str
    chunk_id: str
    page_start: int
    page_end: int
    score: float


class AdmissionQueryResponse(BaseModel):
    answer: str
    citations: List[AdmissionCitation]
    confidence: str
    debug: Optional[Dict[str, Any]] = None
