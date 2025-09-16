"""
Custom exceptions and error handlers for PM Internship AI Engine

This module defines custom exceptions and sets up global error handlers
for the FastAPI application.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Any, Dict, Optional
import traceback

from app.core.config import settings
from app.core.logging import security_logger

logger = logging.getLogger(__name__)


# Custom Exception Classes
class PMInternshipException(Exception):
    """Base exception for PM Internship AI Engine"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(PMInternshipException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(PMInternshipException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class ValidationError(PMInternshipException):
    """Data validation errors"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class NotFoundError(PMInternshipException):
    """Resource not found errors"""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            status_code=404,
            details=details
        )


class ConflictError(PMInternshipException):
    """Resource conflict errors"""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            status_code=409,
            details=details
        )


class RateLimitError(PMInternshipException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429,
            details=details
        )


class AIProcessingError(PMInternshipException):
    """AI processing related errors"""
    
    def __init__(self, message: str = "AI processing failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AI_PROCESSING_ERROR",
            status_code=500,
            details=details
        )


class DatabaseError(PMInternshipException):
    """Database related errors"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class ExternalServiceError(PMInternshipException):
    """External service integration errors"""
    
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details
        )


class FileProcessingError(PMInternshipException):
    """File processing errors"""
    
    def __init__(self, message: str = "File processing failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="FILE_PROCESSING_ERROR",
            status_code=400,
            details=details
        )


class BiasDetectionError(PMInternshipException):
    """Bias detection in AI algorithms"""
    
    def __init__(self, message: str = "Bias detected in algorithm", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="BIAS_DETECTION_ERROR",
            status_code=500,
            details=details
        )


# Error Response Formatter
def format_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Format error response in a consistent structure"""
    
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "status_code": status_code,
            "timestamp": "2024-01-01T00:00:00Z",  # This would be actual timestamp
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if request_id:
        response["error"]["request_id"] = request_id
    
    if settings.DEBUG:
        response["error"]["debug"] = True
    
    return response


# Exception Handlers
async def pm_internship_exception_handler(request: Request, exc: PMInternshipException):
    """Handle custom PM Internship exceptions"""
    
    # Log the exception
    logger.error(
        f"PM Internship Exception: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    # Log security-related exceptions
    if isinstance(exc, (AuthenticationError, AuthorizationError)):
        security_logger.log_suspicious_activity(
            user_id=getattr(request.state, "user_id", "anonymous"),
            activity=exc.error_code,
            details={
                "message": exc.message,
                "path": request.url.path,
                "method": request.method,
                "ip_address": request.client.host if request.client else "unknown"
            }
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            error_code="HTTP_ERROR",
            message=exc.detail,
            status_code=exc.status_code,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    
    logger.warning(
        f"Validation Error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=format_error_response(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=422,
            details={"validation_errors": exc.errors()},
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    
    # Log the full exception with traceback
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        }
    )
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        message = "An internal server error occurred"
        details = None
    else:
        message = str(exc)
        details = {"traceback": traceback.format_exc()}
    
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message=message,
            status_code=500,
            details=details,
            request_id=getattr(request.state, "request_id", None)
        )
    )


def setup_exception_handlers(app: FastAPI):
    """Setup all exception handlers for the FastAPI app"""
    
    # Custom exception handlers
    app.add_exception_handler(PMInternshipException, pm_internship_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers setup completed")


# Utility functions for raising exceptions
def raise_not_found(message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
    """Utility function to raise NotFoundError"""
    raise NotFoundError(message=message, details=details)


def raise_validation_error(message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
    """Utility function to raise ValidationError"""
    raise ValidationError(message=message, details=details)


def raise_authentication_error(message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
    """Utility function to raise AuthenticationError"""
    raise AuthenticationError(message=message, details=details)


def raise_authorization_error(message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
    """Utility function to raise AuthorizationError"""
    raise AuthorizationError(message=message, details=details)


def raise_conflict_error(message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
    """Utility function to raise ConflictError"""
    raise ConflictError(message=message, details=details)