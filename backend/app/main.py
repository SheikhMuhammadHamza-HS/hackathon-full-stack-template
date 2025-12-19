"""FastAPI application entry point."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Hackathon Todo API",
    description="Multi-User Authentication System with JWT",
    version="0.1.0"
)

# Configure CORS
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Hackathon Todo API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


# Import and include routers
from app.routers import auth, tasks, admin

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin (Dev Only)"])
