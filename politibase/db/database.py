"""Database engine and session factory.

Uses SQLite for local development. The schema is designed to be portable
to PostgreSQL + PostGIS for production.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from politibase.models.schema import Base

# Default to a SQLite file in the project data/ directory
_default_db = Path(__file__).resolve().parent.parent.parent / "data" / "politibase.db"
DATABASE_URL = os.environ.get("POLITIBASE_DATABASE_URL", f"sqlite:///{_default_db}")

engine = create_engine(
    DATABASE_URL,
    echo=bool(os.environ.get("POLITIBASE_SQL_ECHO")),
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# Enable WAL mode and foreign keys for SQLite
if "sqlite" in DATABASE_URL:

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a database session (for use as a FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
