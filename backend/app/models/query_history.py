from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.sql import func
from app.db.base import Base


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), index=True, nullable=False)
    question = Column(Text, nullable=False)
    cypher = Column(Text, nullable=True)
    result_columns = Column(JSON, nullable=True)
    result_rows = Column(JSON, nullable=True)
    chart = Column(JSON, nullable=True)
    chart_type = Column(String(30), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
