"""
Logging configuration for PM Internship AI Engine

This module sets up structured logging with different handlers for
development and production environments.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging():
    """Setup structured logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.ENVIRONMENT == "production" 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": settings.LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout,
            },
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "security_file": {
                "level": "WARNING",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/security.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
            },
            "audit_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/audit.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "app.security": {
                "handlers": ["console", "security_file"],
                "level": "WARNING",
                "propagate": False,
            },
            "app.audit": {
                "handlers": ["audit_file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False,
            },
            "celery": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Setup Sentry for error tracking in production
    if settings.SENTRY_DSN and settings.ENVIRONMENT == "production":
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                sentry_logging,
                SqlalchemyIntegration(),
                FastApiIntegration(auto_enable=True),
            ],
            traces_sample_rate=0.1,
            environment=settings.ENVIRONMENT,
        )


class SecurityLogger:
    """Security-focused logger for audit trails"""
    
    def __init__(self):
        self.logger = logging.getLogger("app.security")
    
    def log_authentication_attempt(self, user_id: str, success: bool, ip_address: str):
        """Log authentication attempts"""
        self.logger.warning(
            "Authentication attempt",
            extra={
                "user_id": user_id,
                "success": success,
                "ip_address": ip_address,
                "event_type": "authentication"
            }
        )
    
    def log_authorization_failure(self, user_id: str, resource: str, action: str):
        """Log authorization failures"""
        self.logger.warning(
            "Authorization failure",
            extra={
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "event_type": "authorization"
            }
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str):
        """Log sensitive data access"""
        self.logger.info(
            "Data access",
            extra={
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "event_type": "data_access"
            }
        )
    
    def log_suspicious_activity(self, user_id: str, activity: str, details: dict):
        """Log suspicious activities"""
        self.logger.error(
            "Suspicious activity detected",
            extra={
                "user_id": user_id,
                "activity": activity,
                "details": details,
                "event_type": "suspicious_activity"
            }
        )


class AuditLogger:
    """Audit logger for compliance and tracking"""
    
    def __init__(self):
        self.logger = logging.getLogger("app.audit")
    
    def log_user_action(self, user_id: str, action: str, resource: str, details: dict = None):
        """Log user actions for audit trail"""
        self.logger.info(
            "User action",
            extra={
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "details": details or {},
                "event_type": "user_action"
            }
        )
    
    def log_system_event(self, event: str, details: dict = None):
        """Log system events"""
        self.logger.info(
            "System event",
            extra={
                "event": event,
                "details": details or {},
                "event_type": "system_event"
            }
        )
    
    def log_data_change(self, user_id: str, table: str, record_id: str, 
                       old_values: dict, new_values: dict):
        """Log data changes for audit trail"""
        self.logger.info(
            "Data change",
            extra={
                "user_id": user_id,
                "table": table,
                "record_id": record_id,
                "old_values": old_values,
                "new_values": new_values,
                "event_type": "data_change"
            }
        )
    
    def log_allocation_decision(self, student_id: str, internship_id: str, 
                              decision: str, score: float, reasoning: dict):
        """Log AI allocation decisions for transparency"""
        self.logger.info(
            "Allocation decision",
            extra={
                "student_id": student_id,
                "internship_id": internship_id,
                "decision": decision,
                "score": score,
                "reasoning": reasoning,
                "event_type": "allocation_decision"
            }
        )


class PerformanceLogger:
    """Performance monitoring logger"""
    
    def __init__(self):
        self.logger = logging.getLogger("app.performance")
    
    def log_api_performance(self, endpoint: str, method: str, duration: float, 
                           status_code: int, user_id: str = None):
        """Log API performance metrics"""
        self.logger.info(
            "API performance",
            extra={
                "endpoint": endpoint,
                "method": method,
                "duration": duration,
                "status_code": status_code,
                "user_id": user_id,
                "event_type": "api_performance"
            }
        )
    
    def log_ai_processing_time(self, operation: str, duration: float, 
                              input_size: int, success: bool):
        """Log AI processing performance"""
        self.logger.info(
            "AI processing performance",
            extra={
                "operation": operation,
                "duration": duration,
                "input_size": input_size,
                "success": success,
                "event_type": "ai_performance"
            }
        )


# Create logger instances
security_logger = SecurityLogger()
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)