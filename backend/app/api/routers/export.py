from io import BytesIO
from typing import List
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.repositories.history_repo import get_history
from app.repositories.user_repo import get_by_username
from app.schemas.export import ExportRequest

router = APIRouter(prefix="/export", tags=["export"])
ALLOWED_PERMISSIONS = {
    "data:student",
    "data:course",
    "data:lecturer",
    "data:academic",
}


@router.post("/excel")
def export_excel(payload: ExportRequest, db: Session = Depends(get_db)):
    user = get_by_username(db, payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    permissions = [p for p in (user.permissions or "").split(",") if p]
    if user.role != "admin" and not any(p in ALLOWED_PERMISSIONS for p in permissions):
        raise HTTPException(status_code=403, detail="Không có quyền xuất dữ liệu.")

    columns: List[str] = []
    rows: List[List] = []

    if payload.history_id:
        history = get_history(db, payload.history_id, username=payload.username)
        if not history:
            raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử.")
        columns = history.result_columns or []
        rows = history.result_rows or []
    else:
        columns = payload.columns or []
        rows = payload.rows or []

    if not rows:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để xuất.")

    if not columns and rows:
        columns = [f"Col {idx + 1}" for idx in range(len(rows[0]))]

    df = pd.DataFrame(rows, columns=columns)
    file_name = payload.file_name or "neu_export.xlsx"

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Result")
    buffer.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{file_name}"'
    }
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
