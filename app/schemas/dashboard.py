"""
Dashboard and Statistics Pydantic Schemas for metrics and reporting.
"""
from typing import List
from pydantic import BaseModel
from app.schemas.activity import ActivityResponse


class StatusCount(BaseModel):
    status: str
    count: int


class SourceCount(BaseModel):
    source: str
    count: int


class DashboardStatsResponse(BaseModel):
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    won_leads: int
    lost_leads: int
    conversion_rate: float
    status_distribution: List[StatusCount]
    source_distribution: List[SourceCount]
    recent_activities: List[ActivityResponse]
