from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.log import SystemLog
from app.models.user import User
from app.repositories.log_repo import list_logs


def build_overview(db: Session) -> dict:
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    locked_users = db.query(User).filter(User.is_active.is_(False)).count()
    admin_users = db.query(User).filter(User.role == "admin").count()

    today = datetime.now()
    start_date = datetime(today.year, today.month, today.day) - timedelta(days=6)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
    days = [start_date.date() + timedelta(days=i) for i in range(7)]
    labels = [day.strftime("%d/%m") for day in days]
    created = [0] * 7
    updated = [0] * 7
    deleted = [0] * 7

    weekly_logs = (
        db.query(SystemLog)
        .filter(SystemLog.created_at >= start_date)
        .filter(SystemLog.created_at <= end_date)
        .filter(SystemLog.target == "Tài khoản")
        .order_by(SystemLog.created_at.asc())
        .all()
    )
    for log in weekly_logs:
        if not log.created_at:
            continue
        idx = (log.created_at.date() - days[0]).days
        if idx < 0 or idx >= 7:
            continue
        action = (log.action or "").lower()
        if "thêm" in action:
            created[idx] += 1
        elif "chỉnh" in action or "cập nhật" in action:
            updated[idx] += 1
        elif "xóa" in action:
            deleted[idx] += 1

    total = [created[i] + updated[i] + deleted[i] for i in range(7)]

    logs = list_logs(db)[:5]
    activities = [
        {
            "title": f"#{idx + 1} {log.detail}",
            "date": log.created_at.strftime("%d/%m/%Y"),
        }
        for idx, log in enumerate(logs)
    ]

    return {
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "locked_users": locked_users,
            "admin_users": admin_users,
        },
        "activities": activities,
        "quick_stats": {
            "password_reset_requests": max(0, locked_users // 4),
            "new_users_this_week": max(0, total_users // 30),
            "status_changes": max(0, locked_users // 2),
        },
        "weekly": {
            "labels": labels,
            "created": created,
            "updated": updated,
            "deleted": deleted,
            "total": total,
        },
    }
