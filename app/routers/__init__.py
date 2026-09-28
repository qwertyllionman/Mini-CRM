"""
Routers package initialization.
"""
from app.routers.auth import router as auth_router
from app.routers.leads import router as leads_router
from app.routers.dashboard import router as dashboard_router

__all__ = ["auth_router", "leads_router", "dashboard_router"]
