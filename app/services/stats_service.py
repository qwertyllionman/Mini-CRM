"""
Statistics and dashboard aggregation service.
Computes KPIs, status distributions, source breakdowns, and recent activity streams.
"""
from typing import Dict, Any, List
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models.lead import Lead, LeadStatus
from app.models.activity import LeadActivity
from app.models.user import User


def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """
    Computes real-time CRM performance indicators and distributions.
    """
    total_leads = db.query(Lead).count()

    # Status counts
    status_counts_raw = (
        db.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )
    status_dict = {status.value: 0 for status in LeadStatus}
    for st, count in status_counts_raw:
        if st in status_dict:
            status_dict[st] = count

    new_leads = status_dict.get(LeadStatus.NEW.value, 0)
    contacted_leads = status_dict.get(LeadStatus.CONTACTED.value, 0)
    qualified_leads = status_dict.get(LeadStatus.QUALIFIED.value, 0)
    won_leads = status_dict.get(LeadStatus.WON.value, 0)
    lost_leads = status_dict.get(LeadStatus.LOST.value, 0)

    # Conversion rate: Won / Total * 100
    conversion_rate = round((won_leads / total_leads * 100), 1) if total_leads > 0 else 0.0

    status_distribution = [
        {"status": st, "count": count}
        for st, count in status_dict.items()
    ]

    # Source breakdown
    source_counts_raw = (
        db.query(Lead.source, func.count(Lead.id))
        .group_by(Lead.source)
        .order_by(desc(func.count(Lead.id)))
        .all()
    )
    source_distribution = [
        {"source": src or "Unknown", "count": count}
        for src, count in source_counts_raw
    ]

    # Recent activities (last 10)
    recent_activities_raw = (
        db.query(LeadActivity)
        .order_by(desc(LeadActivity.created_at))
        .limit(10)
        .all()
    )
    
    recent_activities = []
    for act in recent_activities_raw:
        user_name = act.user.full_name if act.user else "Tizim"
        recent_activities.append({
            "id": act.id,
            "lead_id": act.lead_id,
            "user_id": act.user_id,
            "user_name": user_name,
            "action": act.action,
            "old_status": act.old_status,
            "new_status": act.new_status,
            "description": act.description,
            "created_at": act.created_at
        })

    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "contacted_leads": contacted_leads,
        "qualified_leads": qualified_leads,
        "won_leads": won_leads,
        "lost_leads": lost_leads,
        "conversion_rate": conversion_rate,
        "status_distribution": status_distribution,
        "source_distribution": source_distribution,
        "recent_activities": recent_activities
    }
