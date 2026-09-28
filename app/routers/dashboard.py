"""
Dashboard API Router.
Provides aggregated KPIs, charts data, and recent activity logs.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import DashboardStatsResponse
from app.services.stats_service import get_dashboard_stats as get_dashboard_stats_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard metrics:
    - Total, New, Contacted, Qualified, Won, and Lost counts
    - Conversion rate %
    - Status distribution breakdown
    - Source distribution breakdown
    - Top 10 recent CRM activities
    """
    return get_dashboard_stats_service(db=db)
