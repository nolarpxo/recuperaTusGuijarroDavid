from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base


DEFAULT_SQLITE_URL = "sqlite:///identifier.sqlite"


def get_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)
    return raw_url.strip() or DEFAULT_SQLITE_URL


def create_db_engine(url: str | None = None):
    database_url = url or get_database_url()
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, echo=False, future=True, connect_args=connect_args)


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
