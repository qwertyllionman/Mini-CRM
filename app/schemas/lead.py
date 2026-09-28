"""
Lead Pydantic Schemas for creation, updates, and paginated responses.
Includes validation requiring at least email or phone.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator, ConfigDict
from app.models.lead import LeadStatus


class LeadBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Full name or company name of the lead")
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    source: str = Field("Website", min_length=2, max_length=100, description="Lead acquisition channel")
    status: LeadStatus = Field(default=LeadStatus.NEW, description="Current lead status")
    note: Optional[str] = Field(None, description="Freeform notes or requirements")

    @model_validator(mode="after")
    def check_contact_info(self):
        """Validate that at least one of phone or email is provided."""
        has_email = bool(self.email and self.email.strip())
        has_phone = bool(self.phone and self.phone.strip())
        if not has_email and not has_phone:
            raise ValueError("Kamida bitta aloqa ma'lumoti (telefon yoki email) kiritilishi shart.")
        return self


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[LeadStatus] = None
    note: Optional[str] = None


class LeadStatusUpdate(BaseModel):
    status: LeadStatus = Field(..., description="Target status (New, Contacted, Qualified, Won, Lost)")
    note: Optional[str] = Field(None, description="Optional reason or context for the status update")


class LeadResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: str
    status: LeadStatus
    note: Optional[str] = None
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadPaginationResponse(BaseModel):
    items: List[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
