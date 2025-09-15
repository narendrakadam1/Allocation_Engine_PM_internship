"""
Middleware components for PM Internship AI Engine

This module contains custom middleware for request processing, security,
monitoring, and other cross-cutting concerns.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import time
import uuid
import logging
from typing import Callable
import json

from app.core.config import settings
from app.core.logging import security_logger, performance_logger, audit_logger

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Add request timing information"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log performance metrics
        performance_logger.log_api_performance(
            endpoint=request.url.path,
            method=request.method,
            duration=process_time,
            status_code=response.status_code,
            user_id=getattr(request.state, "user_id", None)
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        client_id = user_id or client_ip
        
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            k: v for k, v in self.clients.items()
            if current_time - v["first_request"] < self.period
        }
        
        # Check rate limit
        if client_id in self.clients:
            client_data = self.clients[client_id]
            if client_data["requests"] >= self.calls:
                # Rate limit exceeded
                security_logger.log_suspicious_activity(
                    user_id=user_id or "anonymous",
                    activity="RATE_LIMIT_EXCEEDED",
                    details={
                        "client_ip": client_ip,
                        "requests": client_data["requests"],
                        "period": self.period
                    }
                )
                
                from app.core.exceptions import RateLimitError
                raise RateLimitError("Rate limit exceeded")
            
            client_data["requests"] += 1
        else:
            self.clients[client_id] = {
                "requests": 1,
                "first_request": current_time
            }
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.calls - self.clients[client_id]["requests"])
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.period))
        
        return response


class AuditMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip audit for health checks and static files
        if request.url.path in ["/health", "/metrics"] or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Capture request details
        request_data = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        # Remove sensitive headers
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        for header in sensitive_headers:
            request_data["headers"].pop(header, None)
        
        response = await call_next(request)
        
        # Log the request
        audit_logger.log_user_action(
            user_id=getattr(request.state, "user_id", "anonymous"),
            action=f"{request.method} {request.url.path}",
            resource=request.url.path,
            details={
                "request": request_data,
                "response_status": response.status_code,
                "request_id": getattr(request.state, "request_id", None)
            }
        )
        
        return response


class BiasDetectionMiddleware(BaseHTTPMiddleware):
    """Middleware to detect potential bias in AI decisions"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Check if this is an AI matching endpoint
        if "/api/v1/matching" in request.url.path and response.status_code == 200:
            try:
                # This would integrate with bias detection algorithms
                # For now, we'll just log that bias detection should occur
                logger.info(
                    "Bias detection checkpoint",
                    extra={
                        "endpoint": request.url.path,
                        "user_id": getattr(request.state, "user_id", None),
                        "request_id": getattr(request.state, "request_id", None)
                    }
                )
            except Exception as e:
                logger.error(f"Bias detection error: {e}")
        
        return response


class LanguageMiddleware(BaseHTTPMiddleware):
    """Handle multi-language support"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Detect language from headers or query params
        language = (
            request.query_params.get("lang") or
            request.headers.get("Accept-Language", "en").split(",")[0].split("-")[0]
        )
        
        # Validate language
        if language not in settings.SUPPORTED_LANGUAGES:
            language = settings.DEFAULT_LANGUAGE
        
        # Store language in request state
        request.state.language = language
        
        response = await call_next(request)
        response.headers["Content-Language"] = language
        
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """Response compression middleware"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Add compression hint header
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" in accept_encoding:
            response.headers["Vary"] = "Accept-Encoding"
        
        return response


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Health check and monitoring middleware"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Add health check information to request state
        request.state.health_check_time = time.time()
        
        try:
            response = await call_next(request)
            request.state.health_status = "healthy"
            return response
        except Exception as e:
            request.state.health_status = "unhealthy"
            request.state.health_error = str(e)
            raise


def setup_middleware(app: FastAPI):
    """Setup all middleware for the FastAPI application"""
    
    # Add middleware in reverse order (last added is executed first)
    
    # Health check middleware (should be last)
    app.add_middleware(HealthCheckMiddleware)
    
    # Compression middleware
    app.add_middleware(CompressionMiddleware)
    
    # Language middleware
    app.add_middleware(LanguageMiddleware)
    
    # Bias detection middleware
    if settings.BIAS_DETECTION_ENABLED:
        app.add_middleware(BiasDetectionMiddleware)
    
    # Audit middleware
    app.add_middleware(AuditMiddleware)
    
    # Rate limiting middleware
    app.add_middleware(
        RateLimitMiddleware,
        calls=settings.RATE_LIMIT_PER_MINUTE,
        period=60
    )
    
    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Timing middleware
    app.add_middleware(TimingMiddleware)
    
    # Request ID middleware (should be first)
    app.add_middleware(RequestIDMiddleware)
    
    logger.info("Middleware setup completed")


# Utility functions for middleware
def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host if request.client else "unknown"


def is_safe_path(path: str) -> bool:
    """Check if the path is safe for processing"""
    unsafe_patterns = [
        "../", "..\\", "/etc/", "/proc/", "/sys/",
        "\\windows\\", "\\system32\\", ".env", "config"
    ]
    
    path_lower = path.lower()
    return not any(pattern in path_lower for pattern in unsafe_patterns)