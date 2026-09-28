"""
LeadActivity Pydantic Schemas for audit logging history.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ActivityResponse(BaseModel):
    id: int
    lead_id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
