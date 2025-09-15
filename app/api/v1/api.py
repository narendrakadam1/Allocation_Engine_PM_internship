"""
API v1 Router Configuration

This module sets up the main API router and includes all endpoint routers
for version 1 of the PM Internship AI Engine API.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, students, companies, internships, 
    applications, matching, analytics, notifications,
    documents, admin, health
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    students.router,
    prefix="/students",
    tags=["Students"]
)

api_router.include_router(
    companies.router,
    prefix="/companies",
    tags=["Companies"]
)

api_router.include_router(
    internships.router,
    prefix="/internships",
    tags=["Internships"]
)

api_router.include_router(
    applications.router,
    prefix="/applications",
    tags=["Applications"]
)

api_router.include_router(
    matching.router,
    prefix="/matching",
    tags=["AI Matching"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Administration"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health Checks"]
)