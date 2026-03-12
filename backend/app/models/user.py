from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=True)
    phone = Column(String(30), nullable=True)
    title = Column(String(120), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(String(200), nullable=True)
    department = Column(String(120), nullable=True)
    role = Column(String(20), nullable=False, default="user")
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    permissions = Column(Text, default="")
    reset_token = Column(String(200), nullable=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
