from fastapi import APIRouter, HTTPException, UploadFile, File

from app.schemas.admission import (
    AdmissionImportResponse,
    AdmissionQueryRequest,
    AdmissionQueryResponse,
)
from app.services.admission_service import import_admission_pdf, query_admission

router = APIRouter(prefix="/public/admission", tags=["public-admission"])


@router.post("/import-pdf", response_model=AdmissionImportResponse)
async def import_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file PDF.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File rỗng.")
    try:
        data = import_admission_pdf(file.filename, content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return AdmissionImportResponse(**data)


@router.post("/query", response_model=AdmissionQueryResponse)
def query(payload: AdmissionQueryRequest):
    try:
        data = query_admission(
            question=payload.question,
            lang=payload.language or "vi",
            top_k=payload.top_k,
        )
        return AdmissionQueryResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
