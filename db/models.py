from __future__ import annotations

from typing import Optional

from sqlalchemy import CheckConstraint, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("tipo IN ('cliente', 'empleado')", name="ck_usuarios_tipo"),
        CheckConstraint("trim(dni) <> ''", name="ck_usuarios_dni_not_empty"),
        UniqueConstraint("dni", name="uq_usuarios_dni"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    dni: Mapped[str] = mapped_column(String(20), nullable=False)
    direccion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(160), nullable=False)
    movil: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    tareas_cliente: Mapped[list["Tarea"]] = relationship(
        back_populates="cliente",
        foreign_keys="Tarea.id_cliente",
    )
    tareas_empleado: Mapped[list["Tarea"]] = relationship(
        back_populates="empleado",
        foreign_keys="Tarea.id_empleado",
    )


class Tarea(Base):
    __tablename__ = "tareas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_cliente: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    id_empleado: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    servicio: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    horas: Mapped[int] = mapped_column(nullable=False, default=0)
    precio_hora: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="Pendiente")

    cliente: Mapped[Usuario] = relationship(
        back_populates="tareas_cliente",
        foreign_keys=[id_cliente],
    )
    empleado: Mapped[Usuario] = relationship(
        back_populates="tareas_empleado",
        foreign_keys=[id_empleado],
    )
