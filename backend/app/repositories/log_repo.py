from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.log import SystemLog


def create_log(
    db: Session, actor: str, action: str, target: str, detail: str
) -> SystemLog:
    log = SystemLog(actor=actor, action=action, target=target, detail=detail)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_logs(
    db: Session,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
):
    query = db.query(SystemLog)
    if from_date:
        query = query.filter(SystemLog.created_at >= from_date)
    if to_date:
        query = query.filter(SystemLog.created_at <= to_date)
    if action:
        query = query.filter(SystemLog.action.ilike(f"%{action}%"))
    if actor:
        query = query.filter(SystemLog.actor.ilike(f"%{actor}%"))
    query = query.order_by(SystemLog.created_at.desc())
    if skip:
      query = query.offset(skip)
    if limit:
      query = query.limit(limit)
    return query.all()


def count_logs(
    db: Session,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    action: Optional[str] = None,
    actor: Optional[str] = None,
) -> int:
    query = db.query(SystemLog)
    if from_date:
        query = query.filter(SystemLog.created_at >= from_date)
    if to_date:
        query = query.filter(SystemLog.created_at <= to_date)
    if action:
        query = query.filter(SystemLog.action.ilike(f"%{action}%"))
    if actor:
        query = query.filter(SystemLog.actor.ilike(f"%{actor}%"))
    return query.count()
