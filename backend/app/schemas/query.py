from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    username: str
    question: str
    language: Optional[str] = "vi"
    user_context: Optional[Dict[str, Any]] = None


class QueryChart(BaseModel):
    type: str
    labels: List[Any]
    values: List[Any]


class QueryResponse(BaseModel):
    id: int
    columns: List[str]
    rows: List[List[Any]]
    chart: Optional[QueryChart]
    summary: str
    cypher: Optional[str]
    is_stat: Optional[bool] = None
