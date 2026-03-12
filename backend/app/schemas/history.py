from typing import Any, List, Optional
from datetime import datetime
from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: int
    question: str
    summary: Optional[str]
    chart_type: Optional[str]
    is_data: bool
    created_at: datetime


class HistoryListResponse(BaseModel):
    total: int
    items: List[HistoryItem]


class HistoryDetail(BaseModel):
    id: int
    question: str
    summary: Optional[str]
    columns: List[str]
    rows: List[List[Any]]
    chart: Optional[dict]
    cypher: Optional[str]
    created_at: datetime
