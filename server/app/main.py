"""
FastAPI application entry point for TODO App Demo Server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import auth_router

# Create FastAPI application instance
app = FastAPI(
    title="TODO App Demo Server",
    description="Task management system with user authentication and tag-based organization",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React/Next.js frontend
        "http://localhost:5173",  # Vite frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and Docker health checks.

    Returns:
        dict: Health status with service name and status
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "TODO App Demo Server",
            "version": "0.1.0",
        },
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.

    Returns:
        dict: Welcome message and API documentation links
    """
    return {
        "message": "Welcome to TODO App Demo Server API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# Register API routers
app.include_router(auth_router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup.
    """
    print("🚀 TODO App Demo Server starting...")
    print("📚 API Documentation available at: http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown.
    """
    print("👋 TODO App Demo Server shutting down...")
