from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from db.connection import SessionLocal
from db.models import Usuario


VALID_TYPES = {"cliente", "empleado"}


@dataclass(frozen=True, slots=True)
class EmpleadoListado:
    nombre: str
    email: str
    movil: str
    tipo: str


def normalize_tipo(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized in {"", "todos", "seleccione tipo"}:
        return None

    if normalized not in VALID_TYPES:
        return None

    return normalized


class UsuarioService:
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
        self._session_factory = session_factory

    def list_usuarios(self, tipo: str | None = None) -> list[Usuario]:
        normalized_tipo = normalize_tipo(tipo)

        with self._session_factory() as session:
            stmt = select(Usuario)
            if normalized_tipo is not None:
                stmt = stmt.where(Usuario.tipo == normalized_tipo)
            stmt = stmt.order_by(Usuario.id.asc())
            return list(session.scalars(rfd123
            stmt))

    def list_empleados(self) -> list[Usuario]:
        return self.list_usuarios_por_tipo("empleado")

    def list_usuarios_por_tipo(self, tipo: str) -> list[Usuario]:
        normalized_tipo = normalize_tipo(tipo)
        if normalized_tipo is None:
            return []

        with self._session_factory() as session:
            stmt = (
                select(Usuario)
                .where(Usuario.tipo == normalized_tipo)
                .order_by(func.lower(Usuario.nombre).asc(), Usuario.id.asc())
            )
            return list(session.scalars(stmt))

    def list_empleados_para_informe(self) -> list[EmpleadoListado]:
        with self._session_factory() as session:
            stmt = (
                select(
                    Usuario.nombre,
                    Usuario.email,
                    Usuario.movil,
                    Usuario.tipo,
                )
                .where(Usuario.tipo == "empleado")
                .order_by(func.lower(Usuario.nombre).asc(), Usuario.id.asc())
            )

            return [
                EmpleadoListado(
                    nombre=nombre,
                    email=email,
                    movil=movil or "",
                    tipo=tipo.capitalize(),
                )
                for nombre, email, movil, tipo in session.execute(stmt)
            ]

    def get_usuario(self, user_id: int) -> Usuario | None:
        with self._session_factory() as session:
            return session.get(Usuario, user_id)

    def add_usuario(self, payload: dict[str, Any]) -> Usuario:
        data = self._validate_payload(payload)

        with self._session_factory() as session:
            self._ensure_dni_unique(session, data["dni"])
            usuario = Usuario(**data)
            session.add(usuario)
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ValueError("El DNI ya existe. Debe ser unico.") from exc
            except SQLAlchemyError as exc:
                session.rollback()
                raise ValueError(f"No se pudo anadir el usuario: {exc}") from exc
            session.refresh(usuario)
            return usuario

    def modif_usuario(self, user_id: int, payload: dict[str, Any]) -> Usuario:
        data = self._validate_payload(payload)

        with self._session_factory() as session:
            usuario = session.get(Usuario, user_id)
            if usuario is None:
                raise LookupError("No existe el usuario seleccionado")

            self._ensure_dni_unique(session, data["dni"], exclude_user_id=user_id)
            for key, value in data.items():
                setattr(usuario, key, value)

            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ValueError("El DNI ya existe. Debe ser unico.") from exc
            except SQLAlchemyError as exc:
                session.rollback()
                raise ValueError(f"No se pudo modificar el usuario: {exc}") from exc
            session.refresh(usuario)
            return usuario

    def del_usuario(self, user_id: int) -> None:
        with self._session_factory() as session:
            usuario = session.get(Usuario, user_id)
            if usuario is None:
                raise LookupError("No existe el usuario seleccionado")

            session.delete(usuario)
            try:
                session.commit()
            except SQLAlchemyError as exc:
                session.rollback()
                raise ValueError(
                    "No se pudo eliminar el usuario. Revise si tiene tareas asociadas."
                ) from exc

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
        nombre = (payload.get("nombre") or "").strip()
        dni = (payload.get("dni") or "").strip().upper()
        email = (payload.get("email") or "").strip()
        tipo_input = payload.get("tipo")
        tipo = normalize_tipo(tipo_input)

        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if not dni:
            raise ValueError("El DNI es obligatorio")
        if not email:
            raise ValueError("El email es obligatorio")
        if tipo is None:
            raise ValueError("Debe seleccionar un tipo valido (Cliente o Empleado)")

        return {
            "nombre": nombre,
            "dni": dni,
            "direccion": (payload.get("direccion") or "").strip() or None,
            "email": email,
            "movil": (payload.get("movil") or "").strip() or None,
            "tipo": tipo,
        }

    @staticmethod
    def _ensure_dni_unique(
        session: Session,
        dni: str,
        exclude_user_id: int | None = None,
    ) -> None:
        stmt = select(Usuario.id).where(Usuario.dni == dni)
        if exclude_user_id is not None:
            stmt = stmt.where(Usuario.id != exclude_user_id)

        if session.scalar(stmt) is not None:
            raise ValueError("El DNI ya existe. Debe ser unico.")
