from sqlalchemy.orm import Session
from app.models.settings import AppSettings


def get_settings(db: Session) -> AppSettings:
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, settings: AppSettings, data: dict) -> AppSettings:
    for key, value in data.items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings
