from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.repositories.history_repo import count_history, get_history, list_history
from app.schemas.history import HistoryDetail, HistoryListResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryListResponse)
def history_list(
    username: str,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
):
    items = list_history(db, username=username, limit=limit, skip=skip)
    total = count_history(db, username=username)
    return {
        "total": total,
        "items": [
            {
                "id": item.id,
                "question": item.question,
                "summary": item.summary,
                "chart_type": item.chart_type,
                "is_data": bool(item.cypher),
                "created_at": item.created_at,
            }
            for item in items
        ],
    }


@router.get("/{history_id}", response_model=HistoryDetail)
def history_detail(
    history_id: int,
    username: str,
    db: Session = Depends(get_db),
):
    item = get_history(db, history_id=history_id, username=username)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lịch sử.",
        )
    return {
        "id": item.id,
        "question": item.question,
        "summary": item.summary,
        "columns": item.result_columns or [],
        "rows": item.result_rows or [],
        "chart": item.chart,
        "cypher": item.cypher,
        "created_at": item.created_at,
    }
