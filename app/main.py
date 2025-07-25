# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from contextlib import asynccontextmanager
from .api.v1.medications import router as medications_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Cogitto: Medication AI Assistant started!")
    print("🧠 Intelligent medication management through AI")
    yield
    # Shutdown
    print("👋 Cogitto shutting down")

app = FastAPI(
    title="Cogitto: Medication AI Assistant",
    description="Intelligent medication management through AI",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(medications_router, prefix="/api/v1", tags=["medications"])

@app.get("/")
async def root():
    return {
        "message": "🧠 Cogitto: Medication AI Assistant",
        "version": "1.0.0",
        "description": "Intelligent medication management through AI",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/v1/medications/search?q=acetaminophen",
            "details": "/api/v1/medications/{id}",
            "insights": "/api/v1/medications/{id}/insights"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "cogitto-medication-ai",
        "version": "1.0.0"
    }
