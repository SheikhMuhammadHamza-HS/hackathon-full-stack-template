"""FastAPI application entry point."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Hackathon Todo API",
    description="Multi-User Authentication System with JWT and OAuth",
    version="0.1.0"
)

# Add session middleware for OAuth (must be before CORS)
# Use BETTER_AUTH_SECRET for session signing
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("BETTER_AUTH_SECRET", "development-secret-key-change-in-production"),
    same_site="lax",  # Allow cookies in OAuth redirects
    https_only=False   # Allow HTTP for development (use True in production)
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
