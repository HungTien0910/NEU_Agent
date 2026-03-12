from typing import List
from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_users: int
    active_users: int
    locked_users: int
    admin_users: int


class OverviewActivity(BaseModel):
    title: str
    date: str


class OverviewWeekly(BaseModel):
    labels: List[str]
    created: List[int]
    updated: List[int]
    deleted: List[int]
    total: List[int]


class OverviewResponse(BaseModel):
    stats: OverviewStats
    activities: List[OverviewActivity]
    quick_stats: dict
    weekly: OverviewWeekly
