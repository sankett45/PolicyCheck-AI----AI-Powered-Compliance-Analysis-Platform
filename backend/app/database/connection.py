from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.config import settings

# Create engine with pool_pre_ping enabled to detect disconnected connections
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# Set up local session maker
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency database session generator.
    
    Yields:
        Session: The active database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()