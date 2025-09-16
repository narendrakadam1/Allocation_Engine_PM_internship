"""
Health Check Endpoints

This module provides health check endpoints for monitoring the
PM Internship AI Engine system status and dependencies.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import time
import asyncio
import logging

from app.core.database import db_manager
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: float
    version: str
    environment: str
    uptime: float
    checks: Dict[str, Any]


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model"""
    status: str
    timestamp: float
    version: str
    environment: str
    uptime: float
    system: Dict[str, Any]
    dependencies: Dict[str, Any]
    performance: Dict[str, Any]


# Track application start time
app_start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def basic_health_check():
    """
    Basic health check endpoint
    
    Returns basic system status information for load balancers
    and monitoring systems.
    """
    current_time = time.time()
    uptime = current_time - app_start_time
    
    # Perform basic checks
    checks = {
        "database": await check_database(),
        "cache": await check_cache(),
        "storage": await check_storage(),
    }
    
    # Determine overall status
    status = "healthy" if all(checks.values()) else "unhealthy"
    
    return HealthResponse(
        status=status,
        timestamp=current_time,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        uptime=uptime,
        checks=checks
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint
    
    Returns comprehensive system status including performance metrics,
    dependency status, and system information.
    """
    current_time = time.time()
    uptime = current_time - app_start_time
    
    # System information
    system_info = await get_system_info()
    
    # Dependency checks
    dependencies = await check_all_dependencies()
    
    # Performance metrics
    performance = await get_performance_metrics()
    
    # Determine overall status
    status = "healthy" if dependencies.get("overall", False) else "unhealthy"
    
    return DetailedHealthResponse(
        status=status,
        timestamp=current_time,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        uptime=uptime,
        system=system_info,
        dependencies=dependencies,
        performance=performance
    )


@router.get("/readiness")
async def readiness_check():
    """
    Readiness check for Kubernetes
    
    Checks if the application is ready to serve traffic.
    """
    checks = {
        "database": await check_database(),
        "cache": await check_cache(),
        "ai_models": await check_ai_models(),
    }
    
    if not all(checks.values()):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "checks": checks,
                "message": "Application is not ready to serve traffic"
            }
        )
    
    return {
        "status": "ready",
        "checks": checks,
        "timestamp": time.time()
    }


@router.get("/liveness")
async def liveness_check():
    """
    Liveness check for Kubernetes
    
    Simple check to verify the application is running.
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime": time.time() - app_start_time
    }


# Helper functions for health checks
async def check_database() -> bool:
    """Check database connectivity"""
    try:
        return await db_manager.health_check()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def check_cache() -> bool:
    """Check Redis cache connectivity"""
    try:
        # This would check Redis connectivity
        # For now, return True as placeholder
        return True
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return False


async def check_storage() -> bool:
    """Check file storage connectivity"""
    try:
        # This would check MinIO/S3 connectivity
        # For now, return True as placeholder
        return True
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return False


async def check_ai_models() -> bool:
    """Check AI models availability"""
    try:
        # This would check if AI models are loaded and accessible
        # For now, return True as placeholder
        return True
    except Exception as e:
        logger.error(f"AI models health check failed: {e}")
        return False


async def check_external_services() -> Dict[str, bool]:
    """Check external service connectivity"""
    services = {
        "openai": await check_openai_api(),
        "twilio": await check_twilio_api(),
        "email": await check_email_service(),
        "aadhaar": await check_aadhaar_api(),
    }
    return services


async def check_openai_api() -> bool:
    """Check OpenAI API connectivity"""
    try:
        if not settings.OPENAI_API_KEY:
            return False
        # This would make a test API call
        return True
    except Exception:
        return False


async def check_twilio_api() -> bool:
    """Check Twilio API connectivity"""
    try:
        if not settings.TWILIO_ACCOUNT_SID:
            return False
        # This would make a test API call
        return True
    except Exception:
        return False


async def check_email_service() -> bool:
    """Check email service connectivity"""
    try:
        if not settings.SMTP_HOST:
            return False
        # This would test SMTP connectivity
        return True
    except Exception:
        return False


async def check_aadhaar_api() -> bool:
    """Check Aadhaar API connectivity"""
    try:
        if not settings.AADHAAR_API_URL:
            return False
        # This would make a test API call
        return True
    except Exception:
        return False


async def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    import psutil
    import platform
    
    try:
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent,
            }
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {"error": str(e)}


async def check_all_dependencies() -> Dict[str, Any]:
    """Check all system dependencies"""
    dependencies = {
        "database": await check_database(),
        "cache": await check_cache(),
        "storage": await check_storage(),
        "ai_models": await check_ai_models(),
    }
    
    # Check external services
    external_services = await check_external_services()
    dependencies.update(external_services)
    
    # Calculate overall status
    dependencies["overall"] = all(dependencies.values())
    
    return dependencies


async def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics"""
    try:
        # This would collect actual performance metrics
        return {
            "response_time_avg": 0.05,  # Average response time in seconds
            "requests_per_second": 100,  # Current RPS
            "active_connections": 50,    # Active database connections
            "queue_size": 0,            # Background task queue size
            "error_rate": 0.01,         # Error rate percentage
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return {"error": str(e)}