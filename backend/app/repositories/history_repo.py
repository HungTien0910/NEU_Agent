from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.query_history import QueryHistory


def create_history(
    db: Session,
    username: str,
    question: str,
    cypher: str | None,
    columns: list,
    rows: list,
    chart: dict | None,
    summary: str,
    chart_type: str | None,
) -> QueryHistory:
    item = QueryHistory(
        username=username,
        question=question,
        cypher=cypher,
        result_columns=columns,
        result_rows=rows,
        chart=chart,
        summary=summary,
        chart_type=chart_type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_history(
    db: Session, username: str, limit: int = 20, skip: int = 0
) -> List[QueryHistory]:
    return (
        db.query(QueryHistory)
        .filter(QueryHistory.username == username)
        .order_by(QueryHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_history(db: Session, username: str) -> int:
    return db.query(QueryHistory).filter(QueryHistory.username == username).count()


def get_history(db: Session, history_id: int, username: Optional[str] = None):
    query = db.query(QueryHistory).filter(QueryHistory.id == history_id)
    if username:
        query = query.filter(QueryHistory.username == username)
    return query.first()
