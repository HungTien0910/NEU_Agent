import io
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.log_repo import create_log
from app.services.data_service import (
    build_preview,
    clear_all_data,
    clear_postgres,
    fetch_sheet_items,
    export_sheet_excel,
    export_all_excel,
    create_sheet_item,
    delete_sheet_item,
    update_sheet_item,
    run_import_job,
    count_sheet_items,
    validate_structure,
    validate_excel,
)
from app.services.import_progress import get_progress, set_progress

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/preview")
async def preview_data(
    file: UploadFile = File(...),
    sheet: str = "Student",
    limit: int = 5,
    skip: int = 0,
    search: Optional[str] = None,
):
    content = await file.read()
    structure = validate_structure(content)
    if not structure["ok"]:
        raise HTTPException(status_code=400, detail=structure["message"])
    return build_preview(
        content,
        sheet=sheet,
        limit=limit,
        skip=skip,
        search=search,
        file_name=file.filename or "upload.xlsx",
    )


@router.post("/validate")
async def validate_data(file: UploadFile = File(...)):
    content = await file.read()
    structure = validate_structure(content)
    if not structure["ok"]:
        raise HTTPException(status_code=400, detail=structure["message"])
    return validate_excel(content)


@router.post("/import")
async def import_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    content = await file.read()
    structure = validate_structure(content)
    if not structure["ok"]:
        raise HTTPException(status_code=400, detail=structure["message"])
    job_id = str(uuid.uuid4())
    set_progress(job_id, "running", 0, "Đang chuẩn bị import")
    background_tasks.add_task(run_import_job, job_id, content)
    return {"job_id": job_id, "message": "Import started."}


@router.get("/import/progress")
def import_progress(job_id: str):
    data = get_progress(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình import.")
    return data


@router.post("/clear")
def clear_data(db: Session = Depends(get_db)):
    clear_all_data()
    clear_postgres(db)
    create_log(
        db,
        actor="Admin",
        action="Xóa",
        target="Hệ thống",
        detail="Xóa toàn bộ dữ liệu trên hệ thống.",
    )
    return {"message": "Xóa dữ liệu thành công."}


@router.get("/items")
def list_items(
    sheet: str = "Student",
    search: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db),
):
    return {
        "sheet": sheet,
        "items": fetch_sheet_items(
            db,
            sheet=sheet,
            search=search,
            limit=limit,
            skip=skip,
        ),
        "total": count_sheet_items(db, sheet=sheet, search=search),
        "limit": limit,
        "skip": skip,
    }


@router.put("/items/{sheet}/{item_id}")
def update_item(
    sheet: str, item_id: int, payload: dict, db: Session = Depends(get_db)
):
    try:
        updated = update_sheet_item(db, sheet=sheet, item_id=item_id, payload=payload)
        return updated
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/items/{sheet}")
def create_item(sheet: str, payload: dict, db: Session = Depends(get_db)):
    try:
        created = create_sheet_item(db, sheet=sheet, payload=payload)
        return created
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/items/{sheet}/{item_id}")
def delete_item(sheet: str, item_id: int, db: Session = Depends(get_db)):
    try:
        delete_sheet_item(db, sheet=sheet, item_id=item_id)
        return {"message": "Xóa dữ liệu thành công."}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/export")
def export_sheet(sheet: str, search: Optional[str] = None, db: Session = Depends(get_db)):
    content = export_sheet_excel(db, sheet=sheet, search=search)
    filename = f"neu_{sheet.lower()}_export.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/export-all")
def export_all(db: Session = Depends(get_db)):
    content = export_all_excel(db)
    filename = "neu_all_data_export.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
