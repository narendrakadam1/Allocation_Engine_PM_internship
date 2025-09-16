"""
Database configuration and connection management

This module handles database connections, session management, and provides
utilities for database operations in the PM Internship AI Engine.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy import MetaData
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database URL conversion for async
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif database_url.startswith("sqlite://"):
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

# Create async engine
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    poolclass=StaticPool if "sqlite" in database_url else None,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create declarative base with custom metadata
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

Base = declarative_base(metadata=metadata)


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they are registered
            from app.models import (
                user, student, company, internship, application, 
                matching, notification, document, analytics
            )
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


async def close_db():
    """Close database connections"""
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise


class DatabaseManager:
    """Database manager for handling connections and transactions"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        return self.session_factory()
    
    async def execute_transaction(self, func, *args, **kwargs):
        """Execute a function within a database transaction"""
        async with self.session_factory() as session:
            try:
                result = await func(session, *args, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Transaction error: {e}")
                raise
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.session_factory() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


# Database utilities
class DatabaseUtils:
    """Utility functions for database operations"""
    
    @staticmethod
    async def create_indexes():
        """Create database indexes for performance optimization"""
        try:
            async with engine.begin() as conn:
                # Add custom indexes here
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_students_skills 
                    ON students USING GIN (skills);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_internships_requirements 
                    ON internships USING GIN (requirements);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_applications_status_created 
                    ON applications (status, created_at);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_matching_results_score 
                    ON matching_results (match_score DESC);
                """)
                
                logger.info("Database indexes created successfully")
                
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")
            raise
    
    @staticmethod
    async def backup_database(backup_path: str):
        """Create database backup"""
        try:
            # Implementation depends on database type
            if "postgresql" in settings.DATABASE_URL:
                import subprocess
                subprocess.run([
                    "pg_dump", 
                    settings.DATABASE_URL, 
                    "-f", 
                    backup_path
                ], check=True)
            
            logger.info(f"Database backup created: {backup_path}")
            
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            raise
    
    @staticmethod
    async def get_database_stats():
        """Get database statistics"""
        try:
            async with AsyncSessionLocal() as session:
                stats = {}
                
                # Get table row counts
                tables = [
                    "users", "students", "companies", "internships", 
                    "applications", "matching_results", "notifications"
                ]
                
                for table in tables:
                    result = await session.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = result.scalar()
                
                # Get database size (PostgreSQL specific)
                if "postgresql" in settings.DATABASE_URL:
                    result = await session.execute(
                        "SELECT pg_size_pretty(pg_database_size(current_database()))"
                    )
                    stats["database_size"] = result.scalar()
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


# Export database utilities
db_utils = DatabaseUtils()