from sqlalchemy import Boolean, Column, Integer, String
from app.db.base import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(20), nullable=False, default="vi")
    timezone = Column(String(50), nullable=False, default="GMT+7")
    date_format = Column(String(30), nullable=False, default="DD/MM/YYYY")
    email_notifications = Column(Boolean, default=True)
    error_notifications = Column(Boolean, default=True)
    password_rotation_days = Column(Integer, default=90)
    mfa_enabled = Column(Boolean, default=False)
