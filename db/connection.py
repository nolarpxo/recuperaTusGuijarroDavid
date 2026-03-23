from __future__ import annotations

import os

from sqlalchemy import create_engine, text
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
    _ensure_dni_unique_index()


def _ensure_dni_unique_index() -> None:
    with engine.begin() as connection:
        duplicate_dni = connection.execute(
            text(
                """
                SELECT dni, COUNT(*) AS total
                FROM usuarios
                WHERE dni IS NOT NULL AND TRIM(dni) <> ''
                GROUP BY dni
                HAVING COUNT(*) > 1
                LIMIT 1
                """
            )
        ).first()

        if duplicate_dni is not None:
            raise RuntimeError(
                f"Hay DNIs duplicados en la base de datos: {duplicate_dni[0]}. "
                "Corrige esos registros antes de continuar."
            )

        # Index parcial para no bloquear instalaciones con registros historicos vacios.
        connection.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_dni
                ON usuarios (dni)
                WHERE dni IS NOT NULL AND TRIM(dni) <> ''
                """
            )
        )
