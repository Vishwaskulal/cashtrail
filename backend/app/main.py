from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="CashTrail API",
    description="Predictive Cybercrime Intelligence Platform",
    version="1.0.0"
)

# CORS configuration
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "CashTrail API is running",
        "status": "ok"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cashtrail-backend"
    }

from app.api.predictions import router as predictions_router
from app.api.alerts import router as alerts_router
from app.api.dashboard import router as dashboard_router

app.include_router(predictions_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
