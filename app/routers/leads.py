"""
Leads API Router.
Provides CRUD endpoints, search, filtering, pagination, sorting,
status transitions, and activity audit history.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadStatusUpdate,
    LeadResponse,
    LeadPaginationResponse,
)
from app.schemas.activity import ActivityResponse
from app.services.auth_service import get_current_user_optional, get_current_user
from app.services.lead_service import (
    create_lead as create_lead_service,
    get_leads as get_leads_service,
    get_lead_by_id as get_lead_by_id_service,
    update_lead as update_lead_service,
    update_lead_status as update_lead_status_service,
    delete_lead as delete_lead_service,
    get_lead_activities as get_lead_activities_service,
)

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.get("", response_model=LeadPaginationResponse)
def list_leads(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, email, phone, or note"),
    status: Optional[str] = Query(None, description="Filter by status (New, Contacted, Qualified, Won, Lost)"),
    source: Optional[str] = Query(None, description="Filter by source channel"),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, name, status, source)"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    List leads with full pagination, multi-field search, status filtering,
    source filtering, and dynamic sorting.
    """
    return get_leads_service(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status,
        source_filter=source,
        sort_by=sort_by,
        order=order,
    )


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Create a new lead.
    Requires at least one contact channel (phone or email).
    Automatically records creation activity in the audit history.
    """
    return create_lead_service(db=db, lead_in=lead_in, current_user=current_user)


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Retrieve full details for a single lead by its unique ID.
    """
    return get_lead_by_id_service(db=db, lead_id=lead_id)


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Update lead information (name, contact details, source, status, notes).
    Automatically creates an audit record detailing changed fields.
    """
    return update_lead_service(
        db=db,
        lead_id=lead_id,
        lead_update=lead_update,
        current_user=current_user,
    )


@router.patch("/{lead_id}/status", response_model=LeadResponse)
def update_status(
    lead_id: int,
    status_update: LeadStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Quickly update a lead's pipeline status with an optional note explaining the transition.
    """
    return update_lead_status_service(
        db=db,
        lead_id=lead_id,
        status_update=status_update,
        current_user=current_user,
    )


@router.delete("/{lead_id}")
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Permanently delete a lead and cascade delete its audit history.
    """
    return delete_lead_service(db=db, lead_id=lead_id, current_user=current_user)


@router.get("/{lead_id}/activities", response_model=List[ActivityResponse])
def get_lead_activities(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Retrieve the chronological audit history and activity stream for a lead.
    """
    activities = get_lead_activities_service(db=db, lead_id=lead_id)
    return [
        {
            "id": act.id,
            "lead_id": act.lead_id,
            "user_id": act.user_id,
            "user_name": act.user.full_name if act.user else "Tizim",
            "action": act.action,
            "old_status": act.old_status,
            "new_status": act.new_status,
            "description": act.description,
            "created_at": act.created_at,
        }
        for act in activities
    ]
