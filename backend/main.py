from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import rfp, quick_scan, subconsultants, dashboard, budgets
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="RFP Intelligence Platform",
    description="AI-powered RFP analysis and pursuit decisioning",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quick_scan.router, prefix="/api/quick-scan", tags=["Quick Scan"])
app.include_router(rfp.router, prefix="/api/rfp", tags=["RFP"])
app.include_router(subconsultants.router, prefix="/api/subconsultants", tags=["Sub-Consultants"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
