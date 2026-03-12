from datetime import datetime
from typing import List
from pydantic import BaseModel


class LogItem(BaseModel):
    id: int
    time: datetime
    actor: str
    action: str
    target: str
    detail: str


class LogListResponse(BaseModel):
    total: int
    items: List[LogItem]
