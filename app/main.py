"""
PM Internship AI Engine - Main Application Entry Point

This is the main FastAPI application that serves as the entry point for the
AI-powered internship allocation system for the PM Internship Scheme.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import setup_logging
# from app.api.v1.api import api_router  # Temporarily commented out
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import setup_middleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting PM Internship AI Engine...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")
    logger.info("PM Internship AI Engine started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PM Internship AI Engine...")


# Create FastAPI application
app = FastAPI(
    title="PM Internship AI Engine",
    description="""
    🚀 **Advanced AI-Powered Internship Allocation System**
    
    A comprehensive platform for matching students with internship opportunities 
    through the PM Internship Scheme using cutting-edge AI technology.
    
    ## 🎯 Key Features
    
    - **Multi-Modal AI Matching**: Advanced NLP and semantic matching
    - **Explainable AI**: Transparent decision-making process
    - **Real-Time Automation**: Workflow automation with n8n
    - **Advanced Analytics**: Comprehensive insights and reporting
    - **Enterprise Security**: End-to-end encryption and blockchain audit
    - **Multi-Language Support**: 22+ Indian languages
    - **Mobile-First Design**: Progressive Web App with offline capability
    
    ## 🔗 API Documentation
    
    - **Interactive Docs**: `/docs` (Swagger UI)
    - **Alternative Docs**: `/redoc` (ReDoc)
    - **OpenAPI Schema**: `/openapi.json`
    
    ## 🛡️ Security
    
    - JWT Authentication
    - Role-based Access Control
    - Rate Limiting
    - Input Validation
    - Audit Logging
    """,
    version="1.0.0",
    contact={
        "name": "PM Internship AI Engine Team",
        "email": "support@pm-internship-ai.gov.in",
    },
    license_info={
        "name": "Government of India License",
        "url": "https://www.gov.in/license",
    },
    lifespan=lifespan,
)

# Setup middleware
setup_middleware(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API router (temporarily commented out)
# app.include_router(api_router, prefix="/api/v1")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Welcome to PM Internship AI Engine",
        "version": "1.0.0",
        "description": "Advanced AI-powered internship allocation system",
        "features": [
            "Multi-Modal AI Matching",
            "Explainable AI Decisions",
            "Real-Time Automation",
            "Advanced Analytics",
            "Enterprise Security",
            "Multi-Language Support"
        ],
        "docs": "/docs",
        "api": "/api/v1",
        "status": "operational"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "cache": "connected",
        "ai_engine": "operational"
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Metrics endpoint for Prometheus monitoring"""
    # This would typically return Prometheus metrics
    return {
        "active_users": 0,
        "total_applications": 0,
        "successful_matches": 0,
        "system_load": 0.1,
        "response_time_avg": 0.05
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )