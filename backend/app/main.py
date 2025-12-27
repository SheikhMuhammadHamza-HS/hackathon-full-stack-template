"""FastAPI application entry point."""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Hackathon Todo API",
    description="Multi-User Authentication System with JWT and OAuth and AI Chatbot",
    version="0.2.0"
)


# Custom validation exception handler to log errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging."""
    logger.error(f"Validation error: {exc.errors()}")
    logger.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Custom rate limit exceeded handler for consistent error format
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors with consistent JSON response."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded. Maximum 20 messages per minute.",
            "retry_after": 60
        }
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
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health"
    }


# Import and include routers
from app.routers import auth, tasks, admin, chat, events

# Register chat limiter with app state (required for SlowAPI)
from app.routers.chat import limiter as chat_limiter
app.state.limiter = chat_limiter

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin (Dev Only)"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
# Phase V: Dapr Pub/Sub event handlers
app.include_router(events.router, tags=["Events"])
