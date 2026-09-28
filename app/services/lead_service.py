"""
Lead Service layer.
Encapsulates CRUD operations, pagination, dynamic filtering, sorting,
and automatic audit logging of all lead state changes.
"""
from typing import Optional, Dict, Any, List
from math import ceil
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.lead import Lead, LeadStatus
from app.models.activity import LeadActivity, ActivityAction
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadUpdate, LeadStatusUpdate


def create_lead(db: Session, lead_in: LeadCreate, current_user: Optional[User] = None) -> Lead:
    """
    Creates a new Lead record and logs the initial creation activity.
    """
    lead = Lead(
        name=lead_in.name.strip(),
        email=lead_in.email.strip() if lead_in.email else None,
        phone=lead_in.phone.strip() if lead_in.phone else None,
        source=lead_in.source.strip() if lead_in.source else "Website",
        status=lead_in.status.value if isinstance(lead_in.status, LeadStatus) else lead_in.status,
        note=lead_in.note.strip() if lead_in.note else None,
        owner_id=current_user.id if current_user else None
    )
    db.add(lead)
    db.flush()  # Generate lead.id

    # Create audit log entry
    creator_name = current_user.full_name if current_user else "Tizim"
    activity = LeadActivity(
        lead_id=lead.id,
        user_id=current_user.id if current_user else None,
        action=ActivityAction.CREATED.value,
        old_status=None,
        new_status=lead.status,
        description=f"{creator_name} tomonidan yangi lead '{lead.name}' ({lead.source}) yaratildi."
    )
    db.add(activity)
    db.commit()
    db.refresh(lead)
    return lead


def get_leads(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    source_filter: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc"
) -> Dict[str, Any]:
    """
    Retrieves a paginated list of leads with full-text search, status filter,
    source filter, and customizable sorting.
    """
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10

    query = db.query(Lead)

    # Search filter (name, email, phone, note)
    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Lead.name.ilike(search_term),
                Lead.email.ilike(search_term),
                Lead.phone.ilike(search_term),
                Lead.note.ilike(search_term)
            )
        )

    # Status filter
    if status_filter and status_filter.strip() and status_filter.lower() != "all":
        query = query.filter(Lead.status == status_filter.strip())

    # Source filter
    if source_filter and source_filter.strip() and source_filter.lower() != "all":
        query = query.filter(Lead.source == source_filter.strip())

    # Total count before pagination
    total = query.count()

    # Dynamic sorting
    sort_column_map = {
        "id": Lead.id,
        "name": Lead.name,
        "email": Lead.email,
        "status": Lead.status,
        "source": Lead.source,
        "created_at": Lead.created_at,
        "updated_at": Lead.updated_at,
    }
    sort_column = sort_column_map.get(sort_by, Lead.created_at)
    if order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Apply pagination
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    total_pages = ceil(total / page_size) if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


def get_lead_by_id(db: Session, lead_id: int) -> Lead:
    """
    Finds a single lead by primary key ID or raises a 404 Not Found exception.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{lead_id}-raqamli lead topilmadi."
        )
    return lead


def update_lead(
    db: Session,
    lead_id: int,
    lead_update: LeadUpdate,
    current_user: Optional[User] = None
) -> Lead:
    """
    Updates lead fields and logs an activity audit record detailing changes.
    """
    lead = get_lead_by_id(db, lead_id)
    changes: List[str] = []
    old_status = lead.status

    update_dict = lead_update.model_dump(exclude_unset=True)

    # Check contact validator if email/phone are being modified
    target_email = update_dict.get("email", lead.email)
    target_phone = update_dict.get("phone", lead.phone)
    if not target_email and not target_phone:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Lead kamida bitta aloqa ma'lumotiga (email yoki telefon) ega bo'lishi kerak."
        )

    for field, new_val in update_dict.items():
        old_val = getattr(lead, field)
        if isinstance(new_val, LeadStatus):
            new_val = new_val.value

        if new_val != old_val:
            changes.append(f"{field}: '{old_val}' -> '{new_val}'")
            setattr(lead, field, new_val)

    if changes:
        actor_name = current_user.full_name if current_user else "Tizim"
        action = ActivityAction.STATUS_CHANGED.value if "status" in update_dict and update_dict["status"] != old_status else ActivityAction.UPDATED.value
        
        activity = LeadActivity(
            lead_id=lead.id,
            user_id=current_user.id if current_user else None,
            action=action,
            old_status=old_status if action == ActivityAction.STATUS_CHANGED.value else None,
            new_status=lead.status if action == ActivityAction.STATUS_CHANGED.value else None,
            description=f"{actor_name} tomonidan o'zgartirildi: {', '.join(changes)}"
        )
        db.add(activity)

    db.commit()
    db.refresh(lead)
    return lead


def update_lead_status(
    db: Session,
    lead_id: int,
    status_update: LeadStatusUpdate,
    current_user: Optional[User] = None
) -> Lead:
    """
    Updates only the lead status and records a dedicated STATUS_CHANGED activity.
    """
    lead = get_lead_by_id(db, lead_id)
    target_status = status_update.status.value if isinstance(status_update.status, LeadStatus) else status_update.status

    if lead.status == target_status and not status_update.note:
        return lead

    old_status = lead.status
    lead.status = target_status

    actor_name = current_user.full_name if current_user else "Tizim"
    desc_msg = f"{actor_name} lead statusini '{old_status}'dan '{target_status}'ga o'zgartirdi."
    if status_update.note:
        desc_msg += f" Sabab: {status_update.note}"

    activity = LeadActivity(
        lead_id=lead.id,
        user_id=current_user.id if current_user else None,
        action=ActivityAction.STATUS_CHANGED.value,
        old_status=old_status,
        new_status=target_status,
        description=desc_msg
    )
    db.add(activity)
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: int, current_user: Optional[User] = None) -> Dict[str, str]:
    """
    Deletes a lead and cascades removal of associated activities.
    """
    lead = get_lead_by_id(db, lead_id)
    lead_name = lead.name
    db.delete(lead)
    db.commit()
    return {"message": f"Lead '{lead_name}' (ID: {lead_id}) muvaffaqiyatli o'chirildi."}


def get_lead_activities(db: Session, lead_id: int) -> List[LeadActivity]:
    """
    Retrieves the complete audit trail history for a specific lead.
    """
    get_lead_by_id(db, lead_id)  # Validate lead exists
    activities = (
        db.query(LeadActivity)
        .filter(LeadActivity.lead_id == lead_id)
        .order_by(desc(LeadActivity.created_at))
        .all()
    )
    return activities
