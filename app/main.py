"""
Main FastAPI Application Entrypoint.
Initializes database tables, configures CORS, registers API routers,
and serves the frontend Single-Page Application.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import auth_router, leads_router, dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist upon startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
# Mini-CRM API
Tashkilotlar uchun qulay va to'liq imkoniyatli Lead Management API.

### Imkoniyatlar:
* **Foydalanuvchilar va Autentifikatsiya**: Ro'yxatdan o'tish, tizimga kirish (JWT token).
* **Leadlar boshqaruvi (CRUD)**: Lead yaratish, ko'rish, yangilash va o'chirish.
* **Qidiruv, Filtrlash va Tartiblash**: Ism, email, telefon bo'yicha qidiruv; status va manba bo'yicha filtr; sana, ism, status bo'yicha saralash.
* **Sahifalash (Pagination)**: Sahifa va sahifa hajmi bilan qulay ishlash.
* **Audit va Tarix (Activity Log)**: Har bir lead bo'yicha status va ma'lumotlar o'zgarishi tarixi.
* **Statistika va Dashboard**: Real vaqt ko'rsatkichlari va grafiklar uchun ma'lumotlar.
    """,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(dashboard_router)

# Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def serve_index():
    """Serves the main Single-Page Application interface."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({
        "message": f"Welcome to {settings.PROJECT_NAME} API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    })


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {"status": "healthy", "version": settings.PROJECT_VERSION}
