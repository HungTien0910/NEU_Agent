from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    username: str = Field(..., min_length=1)
    history_id: Optional[int] = None
    columns: Optional[List[str]] = None
    rows: Optional[List[List[Any]]] = None
    file_name: Optional[str] = None
