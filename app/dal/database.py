"""Database engine, session factory, and declarative base

This module is the single point of access for SQLAlchemy infrastructure.
Other modules that need database access should import `Base`, `SessionLocal`, or `engine`
from here; nothing else should construct engines or sessions.

Per ADR 0008, this lives in app/dal/ as part of the Data Access Layer.
"""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ---- External Configuration -----------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

# ---- Engine ---------------------------------------------------------------------------
# `check_same_thread=False` is required for SQLite under FastAPI's threaded
# request handling. Has no effect on non-SQLite database.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

# ---- SQLite Foreign-Key Enforcement ---------------------------------------------------
# SQLite does not enforce foreign key constraints by default. This listener
# issues `PRAGMA foreign_keys=ON` on every new connection so that constraints
# declared in models are actually enforced. No-op for non-SQLite databases.
if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "conncet")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ---- Declarative Base and Session Factory ---------------------------------------------
class Base(DeclarativeBase):
    """Parent class for all SQLAlchemy ORM models in this project."""

    pass


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
