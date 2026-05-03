"""Database configuration for the Reliability Engineer for Health backend.

This module sets up a SQLite database using SQLAlchemy. It exposes
session management helpers and a base class for declarative models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

"""
Database configuration for the Reliability Engineer for Health backend.

The application reads the connection URL from the `DATABASE_URL` environment
variable. If no environment variable is provided it falls back to a
local SQLite database stored in `health_app.db`. When connecting to
SQLite the `check_same_thread` flag is disabled to allow multiple
threads to share a single connection.

To connect to a Postgres instance set `DATABASE_URL` to a URL in the
form `postgresql://user:password@host:port/dbname` and ensure the
appropriate driver (e.g. `psycopg2` or `asyncpg`) is installed. SQLAlchemy
will automatically use the correct driver based on the URL prefix.
"""

# Determine the database URL from the environment or fall back to SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./health_app.db")

# Configure the SQLAlchemy engine. For SQLite we need to set
# `check_same_thread=False` to allow usage from multiple threads. For
# other databases (e.g. Postgres) no special arguments are needed.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL)

# SessionLocal is a factory for new Session objects. Each request
# should use its own session which is committed or rolled back when
# finished.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for model classes. Any class inheriting from Base will
# have a corresponding table created automatically via Base.metadata.create_all().
Base = declarative_base()