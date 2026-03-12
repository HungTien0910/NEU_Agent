from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.repositories.log_repo import create_log
from app.repositories.settings_repo import get_settings, update_settings
from app.schemas.settings import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def read_settings(db: Session = Depends(get_db)):
    settings = get_settings(db)
    return SettingsResponse(**settings.__dict__)


@router.put("", response_model=SettingsResponse)
def write_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    settings = get_settings(db)
    old_values = {
        "language": settings.language,
        "timezone": settings.timezone,
        "date_format": settings.date_format,
        "email_notifications": settings.email_notifications,
        "error_notifications": settings.error_notifications,
        "password_rotation_days": settings.password_rotation_days,
        "mfa_enabled": settings.mfa_enabled,
    }
    data = payload.dict()
    updated = update_settings(db, settings, data)

    field_labels = {
        "language": "Ngôn ngữ",
        "timezone": "Múi giờ",
        "date_format": "Định dạng ngày",
        "email_notifications": "Thông báo email",
        "error_notifications": "Thông báo lỗi",
        "password_rotation_days": "Chu kỳ đổi mật khẩu",
        "mfa_enabled": "Bật MFA",
    }
    changed_fields = [
        label
        for key, label in field_labels.items()
        if data.get(key) != old_values.get(key)
    ]
    if changed_fields:
        detail = f"Cập nhật cài đặt: {', '.join(changed_fields)}"
        create_log(
            db,
            actor="Admin",
            action="Chỉnh sửa",
            target="Cài đặt",
            detail=detail,
        )
    return SettingsResponse(**updated.__dict__)
