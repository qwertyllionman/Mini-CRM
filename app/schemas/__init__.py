"""
Pydantic Schemas package.
"""
from app.schemas.user import UserBase, UserCreate, UserLogin, UserResponse, Token, TokenData
from app.schemas.lead import LeadBase, LeadCreate, LeadUpdate, LeadStatusUpdate, LeadResponse, LeadPaginationResponse
from app.schemas.activity import ActivityResponse
from app.schemas.dashboard import DashboardStatsResponse, StatusCount, SourceCount

__all__ = [
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "LeadBase",
    "LeadCreate",
    "LeadUpdate",
    "LeadStatusUpdate",
    "LeadResponse",
    "LeadPaginationResponse",
    "ActivityResponse",
    "DashboardStatsResponse",
    "StatusCount",
    "SourceCount",
]
