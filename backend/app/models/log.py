from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from app.db.base import Base


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)
    target = Column(String(50), nullable=False)
    detail = Column(String(255), nullable=False)
    actor = Column(String(80), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
