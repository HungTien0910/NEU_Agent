from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.repositories.log_repo import count_logs, list_logs
from app.schemas.log import LogItem, LogListResponse

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=LogListResponse)
def get_logs(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
):
    def parse_date(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    total = count_logs(
        db,
        from_date=parse_date(from_date),
        to_date=parse_date(to_date),
        action=action,
        actor=actor,
    )
    logs = list_logs(
        db,
        from_date=parse_date(from_date),
        to_date=parse_date(to_date),
        action=action,
        actor=actor,
        limit=limit,
        skip=skip,
    )
    return {
        "total": total,
        "items": [
            LogItem(
                id=log.id,
                time=log.created_at,
                actor=log.actor,
                action=log.action,
                target=log.target,
                detail=log.detail,
            )
            for log in logs
        ],
    }
